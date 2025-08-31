from dataclasses import dataclass
import logging
import os
import time
from django.db import transaction
from django.core.files.base import ContentFile

from core.flood_camera_monitoring.application.dto.predict_response import (
    PredictResponse,
)
from core.flood_camera_monitoring.infra.models import Camera, FloodDetectionRecord
from core.flood_camera_monitoring.adapters.gateways.opencv_stream_adapter import (
    OpenCVVideoStream,
)
from core.flood_camera_monitoring.infra.torch_flood_classifier import (
    build_default_classifier,
)


@dataclass
class AnalyzeAllCamerasService:
    """Service to analyze all ACTIVE cameras and persist flood events."""

    # Persist only when there's flood risk with flooded prob >= min_confidence
    # Defaults can be overridden by environment variables
    min_confidence: float = float(os.getenv("FLOOD_MIN_CONFIDENCE", "10.0"))
    sample_frames: int = int(os.getenv("FLOOD_SAMPLE_FRAMES", "3"))
    sample_interval_ms: int = int(os.getenv("FLOOD_SAMPLE_INTERVAL_MS", "150"))
    warmup_drops: int = int(os.getenv("FLOOD_WARMUP_DROPS", "2"))

    def run(self) -> int:
        """
        Analyze all ACTIVE cameras and persist a record with the captured image
        only when flood is predicted with confidence >= min_confidence.
        Returns the number of records saved.
        """
        logger = logging.getLogger(__name__)
        saved = 0
        rows = []  # collect per-câmera resultados para imprimir tabela ao final
        clf = build_default_classifier()

        for cam in Camera.objects.filter(status=Camera.CameraStatus.ACTIVE).iterator():
            stream = OpenCVVideoStream(cam.video_url)
            frames: list[bytes] = []
            try:
                # Drop a few initial frames to reduce buffering artifacts
                for _ in range(max(0, int(self.warmup_drops))):
                    _ = stream.grab()
                attempts = max(1, int(self.sample_frames))
                for i in range(attempts):
                    img_bytes = stream.grab()
                    if img_bytes:
                        frames.append(img_bytes)
                    if i < attempts - 1 and self.sample_interval_ms > 0:
                        time.sleep(self.sample_interval_ms / 1000.0)
            except Exception as e:
                logger.exception(
                    "Failed to grab frames from camera id=%s: %s",
                    getattr(cam, "id", None),
                    e,
                )
            finally:
                stream.close()

            if not frames:
                logger.warning(
                    "No frame captured for camera id=%s. Skipping.",
                    getattr(cam, "id", None),
                )
                continue

            # Predict for all captured frames and aggregate
            assessments: list[PredictResponse] = []
            best_idx = 0
            best_flooded = -1.0
            for idx, fb in enumerate(frames):
                a = clf.predict(fb)
                assessments.append(a)
                flooded = float(a.probabilities.flooded)
                if flooded > best_flooded:
                    best_flooded = flooded
                    best_idx = idx

            mean_normal = sum(float(a.probabilities.normal) for a in assessments) / len(
                assessments
            )
            mean_flooded = sum(
                float(a.probabilities.flooded) for a in assessments
            ) / len(assessments)

            # Decide using best or mean flooded probability
            decision_flooded = max(best_flooded, mean_flooded)
            chosen = assessments[best_idx]
            chosen_bytes = frames[best_idx]

            if decision_flooded >= float(self.min_confidence):
                # Try creating with image; if fails (e.g., permission), save without image
                try:
                    with transaction.atomic():
                        FloodDetectionRecord.objects.create(
                            camera=cam,
                            # Business rule: mark as flooded when flooded prob crosses threshold
                            is_flooded=True,
                            # Store the flooded probability used for the decision as confidence
                            confidence=decision_flooded,
                            prob_normal=mean_normal,
                            prob_flooded=mean_flooded,
                            # Save the exact frame used for the decision with a unique name
                            image=ContentFile(
                                chosen_bytes, name=f"{cam.id}-{int(time.time())}.jpg"
                            ),
                        )
                except Exception as e:
                    logger.warning(
                        "Could not save image for camera id=%s (will save record without image): %s",
                        getattr(cam, "id", None),
                        e,
                    )
                    with transaction.atomic():
                        FloodDetectionRecord.objects.create(
                            camera=cam,
                            is_flooded=True,
                            confidence=decision_flooded,
                            prob_normal=mean_normal,
                            prob_flooded=mean_flooded,
                            image=None,
                        )
                saved += 1
                status = "FLOOD_SAVE"
                logger.info(
                    (
                        "Camera id=%s result: %s | best_flooded=%.2f | mean_flooded=%.2f | "
                        "mean_normal=%.2f | best_conf=%.2f | frames=%d | threshold=%.2f"
                    ),
                    getattr(cam, "id", None),
                    status,
                    best_flooded,
                    mean_flooded,
                    mean_normal,
                    float(chosen.confidence),
                    len(assessments),
                    float(self.min_confidence),
                )
            else:
                status = "NO_FLOOD"
                logger.info(
                    (
                        "Camera id=%s result: %s | best_flooded=%.2f | mean_flooded=%.2f | "
                        "mean_normal=%.2f | best_conf=%.2f | frames=%d | threshold=%.2f"
                    ),
                    getattr(cam, "id", None),
                    status,
                    best_flooded,
                    mean_flooded,
                    mean_normal,
                    float(decision_flooded),
                    len(assessments),
                    float(self.min_confidence),
                )

            # Adiciona linha da tabela
            camera_label = f"({getattr(cam, 'description', '')})".strip()
            rows.append(
                (
                    camera_label,
                    getattr(cam, "video_url", ""),
                    status,
                    f"{float(decision_flooded):.2f}",
                    f"{mean_normal:.2f}",
                    f"{mean_flooded:.2f}",
                )
            )

        # Imprime uma tabela de resumo ao final
        try:
            table = self._format_table(
                ["Câmera", "Endereço", "Status", "Conf(%)", "Normal(%)", "Alagado(%)"],
                rows,
                max_widths={"Endereço": 70},
            )
            logger.info("Resumo da análise (salvos=%s):\n%s", saved, table)
        except Exception:
            logger.exception("Falha ao montar tabela de resumo")

        return saved

    @staticmethod
    def _format_table(headers, rows, max_widths=None) -> str:
        """Gera uma tabela ASCII simples.
        max_widths: dict opcional com largura máxima por coluna (pelo header)
        """
        max_widths = max_widths or {}

        # Calcula larguras
        widths = [len(h) for h in headers]
        for r in rows:
            for i, cell in enumerate(r):
                cell_str = str(cell)
                # aplica truncamento por coluna se definido
                col_name = headers[i]
                limit = max_widths.get(col_name)
                if limit and len(cell_str) > limit:
                    cell_str = cell_str[: max(0, limit - 1)] + "…"
                widths[i] = max(widths[i], len(cell_str))

        def fmt_row(vals):
            out = []
            for i, v in enumerate(vals):
                s = str(v)
                col_name = headers[i]
                limit = max_widths.get(col_name)
                if limit and len(s) > limit:
                    s = s[: max(0, limit - 1)] + "…"
                out.append(s.ljust(widths[i]))
            return " | ".join(out)

        sep = "-+-".join("-" * w for w in widths)
        lines = [fmt_row(headers), sep]
        for r in rows:
            lines.append(fmt_row(r))
        return "\n".join(lines)
