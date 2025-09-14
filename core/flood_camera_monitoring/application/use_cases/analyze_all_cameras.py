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
from core.flood_camera_monitoring.infra.torch_flood_classifier import (
    build_default_classifier,
)
from core.flood_camera_monitoring.application.utils.evaluation import (
    EvalConfig,
    capture_frames,
    aggregate_predictions,
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

    # Early-warning (medium) configuration
    strong_min: float = float(os.getenv("FLOOD_STRONG_MIN", "60.0"))
    medium_min: float = float(os.getenv("FLOOD_MEDIUM_MIN", "25.0"))
    medium_max: float = float(os.getenv("FLOOD_MEDIUM_MAX", "60.0"))
    trend_min_delta: float = float(os.getenv("FLOOD_TREND_MIN_DELTA", "10.0"))
    min_medium_frames: int = int(os.getenv("FLOOD_MIN_MEDIUM_FRAMES", "2"))

    def run_and_collect(self):
        """
        Analyze all ACTIVE cameras, persist flood/medium events when applicable,
        and also collect a presentable summary list for caching and APIs.

        Returns: (results: list[dict], saved: int)
        """
        logger = logging.getLogger(__name__)
        saved = 0
        rows = []  # collect per-câmera resultados para imprimir tabela ao final
        results: list[dict] = []
        clf = build_default_classifier()
        cfg = EvalConfig(
            sample_frames=self.sample_frames,
            sample_interval_ms=self.sample_interval_ms,
            warmup_drops=self.warmup_drops,
            strong_min=self.strong_min,
            medium_min=self.medium_min,
            medium_max=self.medium_max,
            trend_min_delta=self.trend_min_delta,
            min_medium_frames=self.min_medium_frames,
        )

        for cam in Camera.objects.filter(status=Camera.CameraStatus.ACTIVE).iterator():
            # Escolhe a URL correta do stream; o campo antigo 'video_url' foi removido.
            stream_url = getattr(cam, "video_hls", None)
            if not stream_url:
                logger.warning(
                    "Camera id=%s não possui 'video_hls' configurado. Pulando.",
                    getattr(cam, "id", None),
                )
                continue
            try:
                frames = capture_frames(stream_url, cfg)
            except Exception as e:
                logger.exception(
                    "Failed to grab frames from camera id=%s: %s",
                    getattr(cam, "id", None),
                    e,
                )
                frames = []

            if not frames:
                logger.warning(
                    "No frame captured for camera id=%s. Skipping.",
                    getattr(cam, "id", None),
                )
                # Add N/A style result for UI consistency
                results.append(
                    {
                        "camera": {
                            "id": getattr(cam, "id", None),
                            "description": getattr(cam, "description", None),
                        },
                        "is_flooded": False,
                        "confidence": 0.0,
                        "medium": False,
                        "probabilities": {"normal": 0.0, "flooded": 0.0, "medium": 0.0},
                        "meta": {"frames": 0, "note": "no-frame"},
                    }
                )
                continue

            # Predict for all captured frames and aggregate
            summary, assessments = aggregate_predictions(frames, clf, cfg)
            decision_flooded = float(summary["decision_flooded"])  # for logs
            best_flooded = float(summary["best_flooded"])  # for logs
            mean_normal = float(summary["mean_normal"])  # for logs
            mean_flooded = float(summary["mean_flooded"])  # for logs
            mean_medium = float(summary["mean_medium"])  # for logs
            chosen_bytes = summary["chosen_bytes"]
            strong = bool(summary["strong"])  # persist flooded when strong
            medium_condition = bool(summary["medium_flag"]) and not strong

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
                    (
                        "Camera id=%s result: %s | best_flooded=%.2f | mean_flooded=%.2f | "
                        "mean_normal=%.2f | mean_medium=%.2f | best_conf=%.2f | frames=%d | threshold=%.2f"
                    ),
                    getattr(cam, "id", None),
                    status,
                    best_flooded,
                    mean_flooded,
                    mean_normal,
                    mean_medium,
                    decision_flooded,
                    int(summary["frames_count"]),
                    float(self.strong_min),
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
                            image=ContentFile(
                                chosen_bytes, name=f"{cam.id}-{int(time.time())}.jpg"
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
                    (
                        "Camera id=%s result: %s | best_flooded=%.2f | mean_flooded=%.2f | "
                        "mean_normal=%.2f | mean_medium=%.2f | frames=%d | criteria={band:%s,count:%d,trend:%s}"
                    ),
                    getattr(cam, "id", None),
                    status,
                    best_flooded,
                    mean_flooded,
                    mean_normal,
                    mean_medium,
                    int(summary["frames_count"]),
                    str(bool(summary.get("medium_band", False))),
                    int(summary.get("medium_frames", 0)),
                    str(bool(summary["trend"]["rising"])),
                )
            else:
                status = "NO_FLOOD"
                logger.info(
                    (
                        "Camera id=%s result: %s | best_flooded=%.2f | mean_flooded=%.2f | "
                        "mean_normal=%.2f | mean_medium=%.2f | best_conf=%.2f | frames=%d | threshold=%.2f"
                    ),
                    getattr(cam, "id", None),
                    status,
                    best_flooded,
                    mean_flooded,
                    mean_normal,
                    mean_medium,
                    float(decision_flooded),
                    int(summary["frames_count"]),
                    float(self.strong_min),
                )

            camera_label = f"({getattr(cam, 'description', '')})".strip()
            rows.append(
                (
                    camera_label,
                    getattr(cam, "video_hls", ""),
                    status,
                    f"{float(decision_flooded):.2f}",
                    f"{mean_normal:.2f}",
                    f"{mean_flooded:.2f}",
                    f"{mean_medium:.2f}",
                )
            )

            # Append API-friendly result entry
            results.append(
                {
                    "camera": {
                        "id": getattr(cam, "id", None),
                        "description": getattr(cam, "description", None),
                    },
                    "is_flooded": bool(strong),
                    "confidence": float(summary["chosen_confidence"]),
                    "medium": bool(medium_condition and not strong),
                    "probabilities": {
                        "normal": float(mean_normal),
                        "flooded": float(mean_flooded),
                        "medium": float(mean_medium),
                    },
                    "meta": {
                        "frames": int(summary["frames_count"]),
                        "best_flooded": float(best_flooded),
                        "decision_flooded": float(decision_flooded),
                        "trend": summary["trend"],
                    },
                }
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

        return results, saved

    def run(self) -> int:
        """
        Backward-compatible: execute analysis and return only the number of saved records.
        """
        _, saved = self.run_and_collect()
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
