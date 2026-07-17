import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile

from app.services.wheel_classifier import wheel_classifier
from app.services.wheel_rule_engine import evaluate_wheel_prediction


router = APIRouter(
    prefix="/api/wheel-inspection",
    tags=["Wheel Inspection"],
)


BACKEND_DIR = Path(__file__).resolve().parents[3]

UPLOAD_DIR = (
    BACKEND_DIR
    / "uploads"
    / "wheel_inspections"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}


@router.post("/predict")
async def predict_wheel(
    image: UploadFile = File(...),
):
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported image format. "
                "Use JPG, JPEG, PNG or WEBP."
            ),
        )

    extension = Path(
        image.filename or "capture.jpg"
    ).suffix.lower()

    if not extension:
        extension = ".jpg"

    file_name = f"{uuid.uuid4()}{extension}"
    image_path = UPLOAD_DIR / file_name

    try:
        with image_path.open("wb") as buffer:
            shutil.copyfileobj(
                image.file,
                buffer,
            )

        prediction = wheel_classifier.predict(
            image_path
        )

        rule_result = evaluate_wheel_prediction(
            class_name=prediction["class_name"],
            confidence=prediction["confidence"],
        )

        return {
            "success": True,
            "image_name": file_name,
            "prediction": prediction,
            "inspection": rule_result,
        }

    except Exception as error:
        if image_path.exists():
            image_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"Wheel inspection failed: {error}",
        ) from error

    finally:
        await image.close()