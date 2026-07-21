"""
Core inspection workflow endpoint. Implements the pipeline from the spec:

Capture Image -> Quality Validation -> Preprocessing -> AI Detection
-> Rule Engine -> PASS/FAIL Decision -> Reasons -> Report -> Store
"""
from app.services.wheel_classifier import wheel_classifier
from app.services.wheel_rule_engine import evaluate_wheel_prediction

import os
import time
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.config import settings
from app.core.security import get_token_payload, require_roles
from app.models.models import (
    Inspection, Product, User, Defect, InspectionReport, InspectionStatus,
    Severity, SupervisorFeedback, TrainingDataset, VerificationStatus
)
from app.schemas.schemas import (
    InspectionCreateResponse, InspectionOut, SupervisorFeedbackCreate, SupervisorFeedbackOut
)
from app.services.image_processing import validate_and_preprocess, ImageQualityError

from app.services.report_generator import generate_inspection_pdf

router = APIRouter(prefix="/api/inspections", tags=["inspections"])

@router.post("", response_model=InspectionCreateResponse, status_code=201)
async def create_inspection(
    product_id: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    payload: dict = Depends(require_roles("operator", "supervisor", "administrator")),
):
    try:
        print("========== INSPECTION START ==========")

        print("STEP 1 - Looking up product")
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        print("STEP 2 - Saving uploaded image")

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        ext = os.path.splitext(image.filename)[1] or ".jpg"
        filename = f"{uuid.uuid4()}{ext}"
        image_path = os.path.join(settings.UPLOAD_DIR, filename)

        contents = await image.read()

        print("\n========== RECEIVED IMAGE ==========")
        print("Filename :", image.filename)
        print("Content-Type :", image.content_type)
        print("Bytes :", len(contents))
        print("====================================\n")

        if len(contents) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Image exceeds maximum upload size",
            )

        with open(image_path, "wb") as f:
            f.write(contents)

        print("Saved Image:", image_path)
        print("File Exists:", os.path.exists(image_path))
        print("File Size:", os.path.getsize(image_path))

        print(f"Saved image: {image_path}")

        print("STEP 3 - Image validation")
        validate_and_preprocess(image_path)

        print("STEP 4 - AI prediction")

        prediction = wheel_classifier.predict(image_path)

        print("\n========== MODEL OUTPUT ==========")
        print(prediction)
        print("==================================\n")
        print("Prediction:", prediction)

        print("STEP 5 - Rule engine")

        decision = evaluate_wheel_prediction(
            prediction["class_name"],
            prediction["confidence"],
        )
        print("\n========== MODEL OUTPUT ==========")
        print(prediction)
        print("==================================\n")
        print("Decision:", decision)

        start = time.perf_counter()

        inspection_time = round(
            time.perf_counter() - start,
            3,
        )

        status = (
            InspectionStatus.PASS_
            if decision["decision"] == "PASS"
            else InspectionStatus.FAIL
        )

        severity_map = {
            "none": Severity.NONE,
            "minor": Severity.MINOR,
            "medium": Severity.MAJOR,
            "major": Severity.MAJOR,
            "high": Severity.CRITICAL,
            "critical": Severity.CRITICAL,
        }

        severity = severity_map.get(
            decision["severity"].lower(),
            Severity.MAJOR,
        )

        print("STEP 6 - Creating inspection")

        inspection = Inspection(
            product_id=product.id,
            operator_id=payload["sub"],
            image_path=image_path,
            status=status,
            confidence=prediction["confidence_percentage"] / 100,
            severity=severity,
            ai_raw_output=prediction,
            rule_engine_output=decision,
            inspection_time_seconds=inspection_time,
        )

        db.add(inspection)
        db.flush()

        print("Inspection ID:", inspection.id)

        if not decision["passed"]:
            print("STEP 7 - Saving defect")

            defect = Defect(
                inspection_id=inspection.id,
                defect_type="Missing Screw",
                component_name=f'{decision["wheel_type"]} wheel',
                location=None,
                severity=Severity.CRITICAL,
                confidence=prediction["confidence"] / 100,
                suggested_correction=decision["suggested_actions"][0],
            )

            db.add(defect)

        print("STEP 8 - Creating report")

        operator = (
            db.query(User)
            .filter(User.id == payload["sub"])
            .first()
        )

        report_folder = os.path.join(
            settings.UPLOAD_DIR,
            "reports",
        )

        os.makedirs(report_folder, exist_ok=True)

        report_path = os.path.join(
            report_folder,
            f"{inspection.id}.pdf",
        )

        generate_inspection_pdf(
            output_path=report_path,
            image_path=image_path,
            product_name=product.name,
            status=decision["decision"],
            confidence=prediction["confidence_percentage"] / 100,
            severity=decision["severity"],
            reasons=decision["reasons"],
            suggested_actions=decision["suggested_actions"],
            inspection_time_seconds=inspection_time,
            operator_name=operator.full_name or operator.username,
            supervisor_name=None,
            created_at=datetime.utcnow(),
        )

        report = InspectionReport(
            inspection_id=inspection.id,
            pdf_path=report_path,
            summary=f'{decision["decision"]} - {prediction["class_name"]}',
            reasons=decision["reasons"],
            suggested_actions=decision["suggested_actions"],
        )

        db.add(report)

        print("STEP 9 - Commit database")

        db.commit()
        db.refresh(inspection)

        print("========== INSPECTION SUCCESS ==========")

        return InspectionCreateResponse(
            id=inspection.id,
            product_id=inspection.product_id,
            status=inspection.status.value,
            confidence=prediction["confidence_percentage"] / 100,
            severity=inspection.severity.value,
            inspection_time_seconds=inspection.inspection_time_seconds,
            created_at=inspection.created_at,
            defects=inspection.defects,
            reasons=decision["reasons"],
            suggested_actions=decision["suggested_actions"],
        )

    except Exception as e:
        import traceback

        print("\n========== INSPECTION ERROR ==========")
        traceback.print_exc()
        print("ERROR:", str(e))
        print("======================================\n")

        raise
        
@router.get("", response_model=list[InspectionOut])
def list_inspections(
    db: Session = Depends(get_db),
    _payload: dict = Depends(get_token_payload),
    status_filter: str | None = None,
    limit: int = 50,
):
    query = db.query(Inspection).order_by(Inspection.created_at.desc())
    if status_filter:
        query = query.filter(Inspection.status == status_filter)
    return query.limit(limit).all()


@router.get("/{inspection_id}", response_model=InspectionOut)
def get_inspection(inspection_id: str, db: Session = Depends(get_db), _payload=Depends(get_token_payload)):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return inspection


@router.post("/{inspection_id}/feedback", response_model=SupervisorFeedbackOut, status_code=201)
def submit_supervisor_feedback(
    inspection_id: str,
    payload: SupervisorFeedbackCreate,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(require_roles("supervisor", "administrator")),
):
    """
    Supervisor verification step. Verified inspections become eligible
    for the continuous-learning training dataset (see Rule Engine spec section
    'CONTINUOUS LEARNING' — data is never auto-added without this step).
    """
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")

    feedback = SupervisorFeedback(
        inspection_id=inspection_id,
        supervisor_id=token_payload["sub"],
        verification_status=payload.verification_status,
        corrected_label=payload.corrected_label,
        comments=payload.comments,
    )
    db.add(feedback)

    # Add to training dataset only on explicit verification
    if payload.verification_status in (
        VerificationStatus.VERIFIED_CORRECT.value,
        VerificationStatus.VERIFIED_CORRECTED.value,
    ):
        label = payload.corrected_label or inspection.status.value.lower()
        db.add(TrainingDataset(
            inspection_id=inspection.id,
            image_path=inspection.image_path,
            label=label,
            split="train",
        ))

    db.commit()
    db.refresh(feedback)
    return feedback
