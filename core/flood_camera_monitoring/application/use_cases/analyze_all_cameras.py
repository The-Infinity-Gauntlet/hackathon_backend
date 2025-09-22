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
    # Additionally, persist when medium probability is high enough (e.g., 80%)
    medium_min_confidence: float = float(
        os.getenv("FLOOD_MEDIUM_MIN_CONFIDENCE", "80.0")
    )
    sample_frames: int = int(os.getenv("FLOOD_SAMPLE_FRAMES", "3"))
    sample_interval_ms: int = int(os.getenv("FLOOD_SAMPLE_INTERVAL_MS", "150"))
    warmup_drops: int = int(os.getenv("FLOOD_WARMUP_DROPS", "2"))

    # Early-warning (medium) configuration
    strong_min: float = float(os.getenv("FLOOD_STRONG_MIN", "60.0"))
    medium_min: float = float(os.getenv("FLOOD_MEDIUM_MIN", "25.0"))
    medium_max: float = float(os.getenv("FLOOD_MEDIUM_MAX", "60.0"))
    trend_min_delta: float = float(os.getenv("FLOOD_TREND_MIN_DELTA", "10.0"))
    min_medium_frames: int = int(os.getenv("FLOOD_MIN_MEDIUM_FRAMES", "2"))

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
            # Escolhe a URL correta do stream; o campo antigo 'video_url' foi removido.
            stream_url = getattr(cam, "video_hls", None)
            # Pular câmeras de demonstração (loop) para não persistir registros
            if isinstance(stream_url, str) and stream_url.startswith("loop:"):
                logger.info(
                    "Skipping demo loop camera id=%s for persistence.",
                    getattr(cam, "id", None),
                )
                continue
            if not stream_url:
                logger.warning(
                    "Camera id=%s não possui 'video_hls' configurado. Pulando.",
                    getattr(cam, "id", None),
                )
                continue
            stream = OpenCVVideoStream(stream_url)
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
            flooded_series: list[float] = []
            for idx, fb in enumerate(frames):
                a = clf.predict(fb)
                assessments.append(a)
                flooded = float(a.probabilities.flooded)
                if flooded > best_flooded:
                    best_flooded = flooded
                    best_idx = idx
                flooded_series.append(flooded)
            # choose representative frame bytes to persist in records/logs
            chosen_bytes = frames[best_idx] if frames else None

            mean_normal = sum(float(a.probabilities.normal) for a in assessments) / len(
                assessments
            )
            mean_medium = sum(
                float(getattr(a.probabilities, "medium", 0.0)) for a in assessments
            ) / len(assessments)
            mean_flooded = sum(
                float(a.probabilities.flooded) for a in assessments
            ) / len(assessments)
            try:
                mean_medium = sum(
                    float(a.probabilities.medium) for a in assessments
                ) / len(assessments)
            except Exception:
                mean_medium = 0.0
            total = mean_normal + mean_flooded + mean_medium
            if total > 0:
                mean_normal = (mean_normal / total) * 100.0
                mean_flooded = (mean_flooded / total) * 100.0
                mean_medium = 100.0 - (mean_normal + mean_flooded)

            # Decide triggers
            decision_flooded = max(best_flooded, mean_flooded)
            decision_medium = float(mean_medium)

            # Compute early-warning (medium) indicators
            strong = decision_flooded >= float(self.strong_min)
            # rising trend if last increases sufficiently from first
            rising_trend = False
            if len(flooded_series) >= 2:
                rising_trend = (flooded_series[-1] - flooded_series[0]) >= float(
                    self.trend_min_delta
                )
            medium_band = (
                float(self.medium_min) <= mean_flooded < float(self.medium_max)
            )
            medium_frames = sum(
                1
                for v in flooded_series
                if float(self.medium_min) <= v < float(self.strong_min)
            )
            medium_condition = (not strong) and (
                medium_band
                or medium_frames >= int(self.min_medium_frames)
                or (rising_trend and flooded_series[-1] >= float(self.medium_min))
            )

            if strong:
                # Try creating with image; if fails (e.g., permission), save without image
                try:
                    with transaction.atomic():
                        FloodDetectionRecord.objects.create(
                            camera=cam,
                            # Business rule: mark as flooded when flooded prob crosses threshold
                            is_flooded=True,
                            medium=False,
                            # Store the flooded probability used for the decision as confidence
                            confidence=decision_flooded,
                            prob_normal=mean_normal,
                            prob_flooded=mean_flooded,
                            prob_medium=mean_medium,
                            # Save the exact frame used for the decision with a unique name
                            image=(
                                ContentFile(
                                    chosen_bytes,
                                    name=f"{cam.id}-{int(time.time())}.jpg",
                                )
                                if chosen_bytes
                                else None
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
                            medium=False,
                            confidence=decision_flooded,
                            prob_normal=mean_normal,
                            prob_flooded=mean_flooded,
                            prob_medium=mean_medium,
                            image=None,
                        )
                saved += 1
                status = "FLOOD_SAVE"
                logger.info(
                    f"Camera id={getattr(cam, 'id', None)} result: {status} | "
                    f"best_flooded={best_flooded:.2f} | mean_flooded={mean_flooded:.2f} | "
                    f"mean_normal={mean_normal:.2f} | mean_medium={mean_medium:.2f} | "
                    f"best_conf={float(decision_flooded):.2f} | frames={len(assessments)} | "
                    f"threshold={float(self.strong_min):.2f}"
                )
            elif medium_condition:
                # Persist early-warning record (medium)
                try:
                    with transaction.atomic():
                        FloodDetectionRecord.objects.create(
                            camera=cam,
                            is_flooded=False,
                            medium=True,
                            confidence=decision_flooded,
                            prob_normal=mean_normal,
                            prob_flooded=mean_flooded,
                            prob_medium=mean_medium,
                            image=(
                                ContentFile(
                                    chosen_bytes,
                                    name=f"{cam.id}-{int(time.time())}.jpg",
                                )
                                if chosen_bytes
                                else None
                            ),
                        )
                except Exception as e:
                    logger.warning(
                        "Could not save image for camera id=%s (medium, saving without image): %s",
                        getattr(cam, "id", None),
                        e,
                    )
                    with transaction.atomic():
                        FloodDetectionRecord.objects.create(
                            camera=cam,
                            is_flooded=False,
                            medium=True,
                            confidence=decision_flooded,
                            prob_normal=mean_normal,
                            prob_flooded=mean_flooded,
                            prob_medium=mean_medium,
                            image=None,
                        )
                saved += 1
                status = "MEDIUM_SAVE"
                logger.info(
                    f"Camera id={getattr(cam, 'id', None)} result: {status} | "
                    f"best_flooded={best_flooded:.2f} | mean_flooded={mean_flooded:.2f} | "
                    f"mean_normal={mean_normal:.2f} | mean_medium={mean_medium:.2f} | "
                    f"frames={len(assessments)} | criteria={{band:{medium_band},count:{medium_frames},trend:{rising_trend}}}"
                )
            else:
                status = "NO_FLOOD"
                logger.info(
                    f"Camera id={getattr(cam, 'id', None)} result: {status} | "
                    f"best_flooded={best_flooded:.2f} | mean_flooded={mean_flooded:.2f} | "
                    f"mean_normal={mean_normal:.2f} | mean_medium={mean_medium:.2f} | "
                    f"best_conf={float(decision_flooded):.2f} | frames={len(assessments)} | "
                    f"threshold={float(self.strong_min):.2f}"
                )

            camera_label = f"({getattr(cam, 'description', '')})".strip()
            # Keep row length aligned with headers below (7 columns)
            rows.append(
                (
                    camera_label,
                    getattr(cam, "video_hls", ""),
                    status,
                    f"{float(max(decision_flooded, decision_medium)):.2f}",
                    f"{mean_normal:.2f}",
                    f"{mean_flooded:.2f}",
                    f"{mean_medium:.2f}",
                )
            )

        # Imprime uma tabela de resumo ao final
        try:
            table = self._format_table(
                [
                    "Câmera",
                    "Endereço",
                    "Status",
                    "Conf(%)",
                    "Normal(%)",
                    "Alagado(%)",
                    "Médio(%)",
                ],
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
        headers = list(headers)
        ncols = len(headers)
        if ncols == 0:
            return ""

        # Calcula larguras
        widths = [len(str(h)) for h in headers]
        for r in rows:
            # Ajusta por índice; tolera linhas menores/maiores
            for i in range(ncols):
                cell_str = str(r[i]) if i < len(r) else ""
                col_name = headers[i]
                limit = max_widths.get(col_name)
                if limit and len(cell_str) > limit:
                    cell_str = cell_str[: max(0, limit - 1)] + "…"
                widths[i] = max(widths[i], len(cell_str))

        def fmt_row(vals):
            out = []
            for i in range(ncols):
                s = str(vals[i]) if i < len(vals) else ""
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
