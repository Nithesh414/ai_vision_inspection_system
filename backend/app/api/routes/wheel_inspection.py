import shutil
import uuid
import time

from pathlib import Path
from datetime import datetime

from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException,
    Depends
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.models import (
    Inspection,
    InspectionStatus,
    Severity
)

from app.services.wheel_classifier import wheel_classifier

from app.services.wheel_rule_engine import (
    evaluate_wheel_prediction
)


router = APIRouter(
    prefix="/api/wheel-inspection",
    tags=["Wheel Inspection"],
)



BACKEND_DIR = Path(__file__).resolve().parents[3]


UPLOAD_DIR = (
    BACKEND_DIR
    /
    "uploads"
    /
    "wheel_inspections"
)


UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)



ALLOWED_CONTENT_TYPES = {

    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp"

}



# =====================================================
# POST - PREDICT WHEEL
# =====================================================

@router.post("/predict")
async def predict_wheel(
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    start_time = time.perf_counter()


    print(
        "\n================ WHEEL INSPECTION ================"
    )


    print(
        "Filename :",
        image.filename
    )

    print(
        "Content-Type :",
        image.content_type
    )



    if image.content_type not in ALLOWED_CONTENT_TYPES:

        raise HTTPException(

            status_code=400,

            detail=
            "Unsupported image format. Use JPG, JPEG, PNG or WEBP."

        )



    extension = Path(

        image.filename
        or
        "capture.jpg"

    ).suffix.lower()



    if not extension:

        extension = ".jpg"



    file_name = (

        f"{uuid.uuid4()}{extension}"

    )


    image_path = (

        UPLOAD_DIR
        /
        file_name

    )



    try:


        # ================================
        # SAVE IMAGE
        # ================================


        with image_path.open("wb") as buffer:


            shutil.copyfileobj(

                image.file,

                buffer

            )



        print(
            "Saved Image :",
            image_path
        )



        # ================================
        # AI MODEL
        # ================================


        prediction = (

            wheel_classifier.predict(

                str(image_path)

            )

        )


        print(
            "MODEL OUTPUT:",
            prediction
        )



        confidence = prediction.get(

            "confidence",

            0

        )



        # ================================
        # RULE ENGINE
        # ================================


        rule_result = (

            evaluate_wheel_prediction(

                class_name=
                prediction["class_name"],


                confidence=
                confidence

            )

        )


        print(
            "RULE RESULT:",
            rule_result
        )



        inspection_time = round(

            time.perf_counter()
            -
            start_time,

            3

        )



        # ================================
        # STATUS
        # ================================


        status = (

            InspectionStatus.PASS_

            if

            rule_result["decision"]
            ==
            "PASS"

            else

            InspectionStatus.FAIL

        )



        severity_value = (

            rule_result.get(

                "severity",

                "none"

            )

        ).lower()



        severity_map = {


            "none":
            Severity.NONE,


            "minor":
            Severity.MINOR,


            "medium":
            Severity.MAJOR,


            "major":
            Severity.MAJOR,


            "critical":
            Severity.CRITICAL

        }



        severity = severity_map.get(

            severity_value,

            Severity.NONE

        )




        # ================================
        # SAVE INSPECTION DB
        # ================================


        inspection = Inspection(


            image_path=str(image_path),


            status=status,


            confidence=confidence,


            severity=severity,


            ai_raw_output=prediction,


            rule_engine_output=rule_result,


            inspection_time_seconds=
            inspection_time,


            created_at=datetime.utcnow()

        )



        db.add(inspection)

        db.commit()

        db.refresh(inspection)



        print(
            "INSPECTION ID:",
            inspection.id
        )



        return {


            "success": True,


            "inspection_id":
            inspection.id,


            "image_name":
            file_name,


            "prediction":
            prediction,


            "inspection":
            rule_result,


            "database_saved":
            True

        }




    except Exception as error:


        print(
            "ERROR:",
            error
        )


        db.rollback()



        if image_path.exists():

            image_path.unlink()



        raise HTTPException(

            status_code=500,

            detail=f"Wheel inspection failed: {error}"

        )



    finally:


        await image.close()






# =====================================================
# GET INSPECTION RESULT
# =====================================================


@router.get("/inspection/{inspection_id}")
def get_wheel_inspection(

    inspection_id: str,

    db: Session = Depends(get_db)

):


    inspection = (

        db.query(Inspection)

        .filter(

            Inspection.id == inspection_id

        )

        .first()

    )



    if not inspection:


        raise HTTPException(

            status_code=404,

            detail="Inspection not found"

        )



    return {


        "success": True,


        "inspection_id":
        inspection.id,


        "status":

        (

            inspection.status.value

            if inspection.status

            else None

        ),



        "confidence":

        inspection.confidence,



        "severity":

        (

            inspection.severity.value

            if inspection.severity

            else None

        ),



        "image_path":

        inspection.image_path,



        "ai_output":

        inspection.ai_raw_output,



        "rule_engine":

        inspection.rule_engine_output,



        "inspection_time_seconds":

        inspection.inspection_time_seconds,



        "created_at":

        inspection.created_at

    }
