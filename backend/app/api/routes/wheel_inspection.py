import shutil
import uuid
import json

from pathlib import Path

from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException,
    Depends
)

from sqlalchemy.orm import Session


from app.services.wheel_classifier import wheel_classifier

from app.services.wheel_rule_engine import evaluate_wheel_prediction


from app.database import get_db

from app.models.inspection import Inspection




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

    exist_ok=True

)





ALLOWED_CONTENT_TYPES = {

    "image/jpeg",

    "image/jpg",

    "image/png",

    "image/webp",

}





@router.post("/predict")

async def predict_wheel(

    product_id: str,

    image: UploadFile = File(...),

    db: Session = Depends(get_db)

):


    print(
        "\n========== WHEEL INSPECTION =========="
    )



    print(
        "File:",
        image.filename
    )



    if image.content_type not in ALLOWED_CONTENT_TYPES:


        raise HTTPException(

            status_code=400,

            detail=
            "Unsupported image format"

        )




    extension = Path(

        image.filename or "capture.jpg"

    ).suffix.lower()



    if not extension:

        extension=".jpg"





    file_name = (

        f"{uuid.uuid4()}{extension}"

    )



    image_path = (

        UPLOAD_DIR / file_name

    )




    try:


        # ==========================
        # SAVE IMAGE
        # ==========================


        with image_path.open("wb") as buffer:


            shutil.copyfileobj(

                image.file,

                buffer

            )



        print(
            "Image saved:",
            image_path
        )





        # ==========================
        # AI PREDICTION
        # ==========================


        prediction = (

            wheel_classifier.predict(

                str(image_path)

            )

        )



        print(
            "MODEL:",
            prediction
        )





        # ==========================
        # RULE ENGINE
        # ==========================


        rule_result = (

            evaluate_wheel_prediction(

                class_name=
                prediction["class_name"],


                confidence=
                prediction["confidence"]

            )

        )



        print(
            "RULE:",
            rule_result
        )






        # ==========================
        # CREATE INSPECTION RECORD
        # ==========================


        inspection = Inspection(


            product_id=product_id,


            status=

            rule_result.get(

                "status",

                "FAIL"

            ),



            confidence=

            prediction.get(

                "confidence",

                0

            ),



            severity=

            rule_result.get(

                "severity",

                "none"

            ),




            image_path=

            str(

                image_path.relative_to(

                    BACKEND_DIR

                )

            ),



            defects=

            json.dumps(

                rule_result.get(

                    "defects",

                    []

                )

            ),



            reasons=

            json.dumps(

                rule_result.get(

                    "reasons",

                    []

                )

            ),




            suggested_actions=

            json.dumps(

                rule_result.get(

                    "suggested_actions",

                    []

                )

            )

        )





        db.add(inspection)


        db.commit()


        db.refresh(inspection)





        print(

            "Inspection saved:",

            inspection.id

        )






        return {


            "success":True,


            "inspection_id":

            inspection.id,



            "prediction":

            prediction,



            "inspection":

            rule_result


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

            detail=

            f"Wheel inspection failed: {error}"

        )



    finally:


        await image.close()
