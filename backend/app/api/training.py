from fastapi import APIRouter, UploadFile, File, Form
import shutil
import uuid
from pathlib import Path

router = APIRouter(
    prefix="/api/training",
    tags=["Training"]
)

UPLOAD_DIR = Path("uploads/training")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DATASET = []

@router.post("/upload")
async def upload_training_sample(
    image: UploadFile = File(...),
    product_id: str = Form(...),
    label: str = Form(...),
    notes: str = Form("")
):

    filename = f"{uuid.uuid4()}.jpg"

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
        "success": True
    }

@router.get("")
def list_dataset():
    return DATASET
