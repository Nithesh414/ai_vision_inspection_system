from fastapi import APIRouter, UploadFile, File, Form
import shutil
import uuid
import random
import time
from pathlib import Path

router = APIRouter(
    prefix="/api/training",
    tags=["Training"]
)

UPLOAD_DIR = Path("uploads/training")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DATASET = []

training_status = {
    "running": False,
    "completed": False,
    "progress": 0,
    "epoch": 0,
    "accuracy": 0,
    "loss": 0,
    "model_version": "v1.0"
}


# ===============================
# Upload Training Image
# ===============================
@router.post("/upload")
async def upload_training_sample(
    image: UploadFile = File(...),
    product_id: str = Form(...),
    label: str = Form(...),
    notes: str = Form("")
):

    extension = Path(image.filename).suffix or ".jpg"

    filename = f"{uuid.uuid4()}{extension}"

    path = UPLOAD_DIR / filename

    with open(path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    DATASET.append({
        "id": str(uuid.uuid4()),
        "product_id": product_id,
        "product_name": product_id,
        "label": label,
        "notes": notes,
        "image_url": f"/uploads/training/{filename}",
        "created_at": "Just Now"
    })

    return {
        "success": True,
        "message": "Training sample uploaded successfully"
    }


# ===============================
# Dataset
# ===============================
@router.get("/dataset")
def list_dataset():
    return {
        "total_images": len(DATASET),
        "dataset": DATASET
    }


# ===============================
# Fake Training
# ===============================
@router.post("/start")
def start_training():

    training_status["running"] = True
    training_status["completed"] = False

    for epoch in range(1, 11):

        time.sleep(0.5)

        training_status["epoch"] = epoch
        training_status["progress"] = epoch * 10

        training_status["accuracy"] = round(
            random.uniform(90, 99),
            2,
        )

        training_status["loss"] = round(
            random.uniform(0.05, 0.30),
            3,
        )

    training_status["running"] = False
    training_status["completed"] = True

    current = float(training_status["model_version"][1:])
    training_status["model_version"] = f"v{current + 0.1:.1f}"

    return {
        "success": True,
        "message": "Model Training Completed",
        "model_version": training_status["model_version"],
        "accuracy": training_status["accuracy"]
    }


# ===============================
# Training Status
# ===============================
@router.get("/status")
def training_progress():
    return training_status
