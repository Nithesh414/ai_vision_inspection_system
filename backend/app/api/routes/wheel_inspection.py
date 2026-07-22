"""
Wheel Inspection Endpoint

Flow:

Image Upload
      |
      v
AI Wheel Classification
      |
      v
Rule Engine
      |
      v
Inspection Table
      |
      v
Defect + PDF Report
"""


import os
import shutil
import uuid
import time


from pathlib import Path
from datetime import datetime


from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException
)


from sqlalchemy.orm import Session


from app.db.session import get_db

from app.core.security import require_roles

from app.core.config import settings


from app.models.models import (

    Inspection,

    Product,

    Defect,

    InspectionReport,

    InspectionStatus,

    Severity,

    User

)


from app.services.wheel_classifier import wheel_classifier

from app.services.wheel_rule_engine import evaluate_wheel_prediction

from app.services.report_generator import generate_inspection_pdf




router = APIRouter(

    prefix="/api/wheel-inspection",

    tags=["Wheel Inspection"]

)



UPLOAD_DIR = (

    Path(settings.UPLOAD_DIR)

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

    product_id: str | None = Form(None),

    db: Session = Depends(get_db),

    payload: dict = Depends(

        require_roles(

            "operator",

            "supervisor",

            "administrator"

        )

    )

):


    start_time = time.perf_counter()


    try:


        print(
            "========== WHEEL INSPECTION START =========="
        )



        # ======================================
        # PRODUCT HANDLING
        # ======================================


        product = None


        if (

            product_id

            and

            product_id.strip()

            and

            product_id.lower() != "string"

        ):


            product = (

                db.query(Product)

                .filter(
                    Product.id == product_id
                )

                .first()

            )


            if not product:


                raise HTTPException(

                    status_code=404,

                    detail="Product not found"

                )


        else:


            # Default product


            product = (

                db.query(Product)

                .filter(

                    Product.name ==
                    "Wheel Inspection"

                )

                .first()

            )


            if not product:


                product = Product(

                    name="Wheel Inspection",

                    code="AUTO-WHEEL",

                    description="AI Wheel Inspection",

                    specification="Wheel defect detection"

                )


                db.add(product)

                db.flush()



        print(

            "PRODUCT:",

            product.name

        )





        # ======================================
        # IMAGE VALIDATION
        # ======================================


        if image.content_type not in ALLOWED_CONTENT_TYPES:


            raise HTTPException(

                status_code=400,

                detail="Invalid image format"

            )





        # ======================================
        # SAVE IMAGE
        # ======================================


        extension = (

            Path(

                image.filename

                or

                "wheel.jpg"

            )

            .suffix

        )


        if not extension:

            extension=".jpg"



        filename = (

            f"{uuid.uuid4()}{extension}"

        )



        image_path = (

            UPLOAD_DIR

            /

            filename

        )



        with image_path.open("wb") as buffer:


            shutil.copyfileobj(

                image.file,

                buffer

            )



        print(

            "IMAGE:",

            image_path

        )





        # ======================================
        # AI PREDICTION
        # ======================================


        prediction = (

            wheel_classifier.predict(

                str(image_path)

            )

        )


        print(

            "MODEL:",

            prediction

        )





        confidence = prediction.get(

            "confidence",

            0

        )



        if prediction.get(

            "confidence_percentage"

        ):


            confidence = (

                prediction["confidence_percentage"]

                /

                100

            )







        # ======================================
        # RULE ENGINE
        # ======================================


        decision = (

            evaluate_wheel_prediction(

                prediction["class_name"],

                confidence

            )

        )



        print(

            "DECISION:",

            decision

        )





        inspection_time = round(

            time.perf_counter()

            -

            start_time,

            3

        )






        # ======================================
        # STATUS
        # ======================================


        status = (

            InspectionStatus.PASS_

            if

            decision["decision"]=="PASS"

            else

            InspectionStatus.FAIL

        )




        severity_map = {


            "none": Severity.NONE,

            "minor": Severity.MINOR,

            "medium": Severity.MAJOR,

            "major": Severity.MAJOR,

            "critical": Severity.CRITICAL


        }



        severity = severity_map.get(

            decision.get(

                "severity",

                "major"

            ).lower(),

            Severity.MAJOR

        )






        # ======================================
        # SAVE INSPECTION
        # ======================================


        inspection = Inspection(


            product_id=product.id,


            operator_id=payload["sub"],


            image_path=str(image_path),


            status=status,


            confidence=confidence,


            severity=severity,


            ai_raw_output=prediction,


            rule_engine_output=decision,


            inspection_time_seconds=inspection_time


        )



        db.add(inspection)


        db.flush()



        print(

            "INSPECTION ID:",

            inspection.id

        )







        # ======================================
        # DEFECT SAVE
        # ======================================


        if not decision["passed"]:


            defect = Defect(


                inspection_id=inspection.id,


                defect_type=prediction["class_name"],


                component_name="Wheel",


                severity=severity,


                confidence=confidence,


                suggested_correction=(

                    decision.get(

                        "suggested_actions",

                        [

                            "Manual inspection"

                        ]

                    )[0]

                )


            )


            db.add(defect)






        # ======================================
        # PDF REPORT
        # ======================================


        report_folder = os.path.join(

            settings.UPLOAD_DIR,

            "reports"

        )


        os.makedirs(

            report_folder,

            exist_ok=True

        )



        pdf_path = os.path.join(

            report_folder,

            f"{inspection.id}.pdf"

        )



        operator = (

            db.query(User)

            .filter(

                User.id == payload["sub"]

            )

            .first()

        )





        generate_inspection_pdf(


            output_path=pdf_path,


            image_path=str(image_path),


            product_name=product.name,


            status=decision["decision"],


            confidence=confidence,


            severity=severity.value,


            reasons=decision.get(

                "reasons",

                []

            ),


            suggested_actions=decision.get(

                "suggested_actions",

                []

            ),


            inspection_time_seconds=inspection_time,


            operator_name=(

                operator.full_name

                if operator

                else

                "Operator"

            ),


            supervisor_name=None,


            created_at=datetime.utcnow()


        )





        report = InspectionReport(


            inspection_id=inspection.id,


            pdf_path=pdf_path,


            summary=(

                f"{decision['decision']} - "

                f"{prediction['class_name']}"

            ),


            reasons=decision.get(

                "reasons",

                []

            ),


            suggested_actions=decision.get(

                "suggested_actions",

                []

            )


        )



        db.add(report)





        db.commit()


        db.refresh(inspection)





        print(

            "========== SUCCESS =========="

        )





        return {


            "success":True,


            "inspection_id":inspection.id,


            "product":{

                "id":product.id,

                "name":product.name

            },


            "status":inspection.status.value,


            "confidence":inspection.confidence,


            "severity":inspection.severity.value,


            "prediction":prediction,


            "inspection":decision


        }





    except HTTPException:

        raise





    except Exception as e:


        print(

            "ERROR:",

            e

        )


        db.rollback()



        raise HTTPException(

            status_code=500,

            detail=str(e)

        )




    finally:


        await image.close()
