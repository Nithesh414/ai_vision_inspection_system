"""
Periodic Retraining Script
============================
Run manually or via a scheduled job (cron / Airflow / etc.) once enough
supervisor-verified data has accumulated in TrainingDataset.

Usage:
    python train.py --module defect_detection --epochs 100

This is a starting point: it wires up YOLO training with the augmentation
strategy from the spec (rotation, brightness, contrast, flip, zoom, noise,
blur via Albumentations) and expects data in YOLO format under
ai_models/dataset/<module>/{train,validation,test}.

After training completes, register the new weights as a ModelVersion row
(via the /api/models endpoints or directly in the DB) and activate it once
validated — this script does not auto-deploy the model.
"""
import argparse
import os

from ultralytics import YOLO


def train(module: str, epochs: int, imgsz: int, data_yaml: str, base_model: str = "yolov8n.pt"):
    print(f"[train] Starting training for module='{module}' using {data_yaml}")
    model = YOLO(base_model)

    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        patience=15,
        project="ai_models/runs",
        name=module,
        # Built-in Ultralytics augmentations covering the spec's list
        # (rotation, brightness/contrast via hsv, flip, zoom via scale, blur/noise via mosaic+erasing)
        degrees=10.0,
        hsv_h=0.015,
        hsv_s=0.5,
        hsv_v=0.4,
        fliplr=0.5,
        scale=0.3,
        mosaic=1.0,
        erasing=0.2,
    )

    best_weights = os.path.join("ai_models/runs", module, "weights", "best.pt")
    print(f"[train] Training complete. Best weights at: {best_weights}")
    print("[train] Next steps: copy weights into ai_models/weights/ and register a "
          "ModelVersion via POST /api/models (or a DB insert), then activate it.")
    return best_weights


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrain a detection module")
    parser.add_argument("--module", required=True, choices=["product_detection", "component_detection", "defect_detection"])
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--data", default=None, help="Path to YOLO data.yaml (defaults to ai_models/<module>_data.yaml)")
    args = parser.parse_args()

    data_yaml = args.data or f"ai_models/{args.module}_data.yaml"
    train(args.module, args.epochs, args.imgsz, data_yaml)
