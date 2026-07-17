"""
AI Inference Service
=====================
Wraps the three detection modules described in the spec:

  Module 1 - Product Detection      (confirms the correct product is in frame)
  Module 2 - Component Detection    (detects each required component + count)
  Module 3 - Defect Detection       (scratch, crack, dent, rust, broken, etc.)
  Module 4 - Assembly Validation    (position/orientation checks, done partly
                                      here via geometry, and partly in the
                                      rule engine which owns tolerance logic)

Each module loads a YOLO (ultralytics) model if weights are present on disk.
If no trained weights exist yet (fresh install, before first training run),
the service falls back to a stub detector so the API remains fully
functional for development/demo purposes. Swap in real trained weights by
dropping them into MODEL_DIR with the filenames configured in core/config.py.
"""
import os
import time
from typing import Any

import numpy as np

from app.core.config import settings

try:
    from ultralytics import YOLO
    _ULTRALYTICS_AVAILABLE = True
except Exception:
    _ULTRALYTICS_AVAILABLE = False


class DetectionModule:
    """Thin wrapper around a YOLO model for one detection task."""

    def __init__(self, weights_filename: str, label: str):
        self.label = label
        self.weights_path = os.path.join(settings.MODEL_DIR, weights_filename)
        self.model = None
        if _ULTRALYTICS_AVAILABLE and os.path.exists(self.weights_path):
            self.model = YOLO(self.weights_path)

    @property
    def is_trained(self) -> bool:
        return self.model is not None

    def predict(self, image_path: str) -> list[dict[str, Any]]:
        """
        Returns a list of detections:
        [{"class": "bolt", "confidence": 0.94, "bbox": [x1,y1,x2,y2]}, ...]
        """
        if self.model is not None:
            results = self.model.predict(source=image_path, conf=settings.CONFIDENCE_THRESHOLD, verbose=False)
            detections = []
            for r in results:
                names = r.names
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    detections.append({
                        "class": names[cls_id],
                        "confidence": float(box.conf[0]),
                        "bbox": [float(v) for v in box.xyxy[0]],
                    })
            return detections

        # ---- Stub fallback (no trained weights yet) ----
        return self._stub_predict(image_path)

    def _stub_predict(self, image_path: str) -> list[dict[str, Any]]:
        """
        Deterministic placeholder so the pipeline is runnable end-to-end
        before a real model has been trained. Replace once weights exist.
        """
        return []


class AIInferenceService:
    """Coordinates all detection modules for a single inspection."""

    def __init__(self):
        self.product_detector = DetectionModule(settings.PRODUCT_DETECTION_MODEL, "product_detection")
        self.component_detector = DetectionModule(settings.COMPONENT_DETECTION_MODEL, "component_detection")
        self.defect_detector = DetectionModule(settings.DEFECT_DETECTION_MODEL, "defect_detection")

    def run_full_pipeline(self, image_path: str, expected_product_code: str) -> dict[str, Any]:
        """
        Runs Modules 1-3 sequentially and returns a structured raw-AI-output
        dict that the Rule Engine (services/rule_engine.py) will evaluate.
        This function does NOT decide PASS/FAIL — that is the rule engine's job.
        """
        start = time.perf_counter()

        product_detections = self.product_detector.predict(image_path)
        component_detections = self.component_detector.predict(image_path)
        defect_detections = self.defect_detector.predict(image_path)

        elapsed = round(time.perf_counter() - start, 3)

        return {
            "product_detections": product_detections,
            "component_detections": component_detections,
            "defect_detections": defect_detections,
            "modules_trained": {
                "product_detection": self.product_detector.is_trained,
                "component_detection": self.component_detector.is_trained,
                "defect_detection": self.defect_detector.is_trained,
            },
            "inference_time_seconds": elapsed,
        }


# Singleton instance used by API routes
ai_service = AIInferenceService()
