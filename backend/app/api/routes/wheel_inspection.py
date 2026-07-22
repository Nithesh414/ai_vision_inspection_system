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
from app.core.security import get_token_payload
from sqlalchemy.orm import Session


from app.db.session import get_db


from app.models.models import (
    Inspection,
    Product,
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




@router.post("/predict")
async def predict_wheel(

    image: UploadFile = File(...),

    db: Session = Depends(get_db),

    payload: dict = Depends(get_token_payload)

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

            detail=(
                "Unsupported image format. "
                "Use JPG, JPEG, PNG or WEBP."
            )

        )



    extension = Path(

        image.filename
        or
        "capture.jpg"

    ).suffix.lower()



    if not extension:

        extension=".jpg"



    file_name = (

        f"{uuid.uuid4()}{extension}"

    )



    image_path = (

        UPLOAD_DIR
        /
        file_name

    )



    try:


        # ============================
        # SAVE IMAGE
        # ============================


        with image_path.open("wb") as buffer:


            shutil.copyfileobj(

                image.file,

                buffer

            )



        print(
            "Saved Image :",
            image_path
        )


        print(
            "File Exists :",
            image_path.exists()
        )


        print(
            "File Size :",
            image_path.stat().st_size,
            "bytes"
        )




        # ============================
        # AI PREDICTION
        # ============================


        prediction = wheel_classifier.predict(

            str(image_path)

        )


        print(
            "\n========== MODEL OUTPUT =========="
        )


        print(prediction)



        # ============================
        # RULE ENGINE
        # ============================


        rule_result = evaluate_wheel_prediction(

            class_name=
            prediction["class_name"],


            confidence=
            prediction["confidence"]

        )


        print(
            "\n========== RULE ENGINE =========="
        )


        print(rule_result)




        inspection_time = round(

            time.perf_counter()
            -
            start_time,

            3

        )




        # ============================
        # GET DEFAULT PRODUCT
        # ============================


        product = (

            db.query(Product)

            .filter(

                Product.code=="AUTO-WHEEL"

            )

            .first()

        )



        if not product:

            raise HTTPException(

                status_code=404,

                detail="Wheel product not found"

            )





        # ============================
        # SAVE INSPECTION
        # ============================


        status = (

            InspectionStatus.PASS_

            if rule_result["decision"]=="PASS"

            else InspectionStatus.FAIL

        )



        severity = Severity.NONE



        inspection = Inspection(

            product_id=product.id,


            operator_id=payload["sub"],


            image_path=str(image_path),


            status=status,


            confidence=prediction["confidence"],


            severity=severity,


            ai_raw_output=prediction,


            rule_engine_output=rule_result,


            inspection_time_seconds=inspection_time,


            created_at=datetime.utcnow()

        )



        db.add(inspection)


        db.commit()


        db.refresh(inspection)



        print(

            "Inspection ID:",

            inspection.id

        )



        print(
            "=================================\n"
        )



        # ============================
        # SAME RESPONSE FORMAT
        # ============================


        return {


            "success": True,


            "image_name": file_name,


            "inspection_id":
            inspection.id,


            "prediction": prediction,


            "inspection": rule_result

        }




    except Exception as error:


        print(
            "ERROR :",
            error
        )



        db.rollback()



        if image_path.exists():

            image_path.unlink()



        raise HTTPException(

            status_code=500,

            detail=f"Wheel inspection failed: {error}"

        ) from error




    finally:

        await image.close()
