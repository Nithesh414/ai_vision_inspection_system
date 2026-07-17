"""
Model Version Management + Continuous Learning Queue.

Continuous learning is deliberately NOT automatic per the spec: verified
inspection data accumulates in TrainingDataset, and an administrator/supervisor
must explicitly trigger a retraining job, which is tracked in RetrainingQueue.
The actual training loop is run out-of-process (see ai_models/train.py) and
would update RetrainingQueue.status + create a new ModelVersion when done.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import ModelVersion, RetrainingQueue, TrainingDataset
from app.schemas.schemas import ModelVersionOut, RetrainingQueueOut
from app.core.security import require_roles

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("/versions", response_model=list[ModelVersionOut])
def list_model_versions(db: Session = Depends(get_db), _user=Depends(require_roles("administrator", "supervisor"))):
    return db.query(ModelVersion).order_by(ModelVersion.trained_at.desc()).all()


@router.post("/versions/{version_id}/activate", response_model=ModelVersionOut)
def activate_model_version(
    version_id: str, db: Session = Depends(get_db), _user=Depends(require_roles("administrator"))
):
    version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Model version not found")

    db.query(ModelVersion).filter(ModelVersion.module == version.module).update({"is_active": False})
    version.is_active = True
    db.commit()
    db.refresh(version)
    return version


@router.post("/retrain", response_model=RetrainingQueueOut, status_code=201)
def trigger_retraining(
    db: Session = Depends(get_db), token_payload: dict = Depends(require_roles("administrator", "supervisor"))
):
    dataset_count = db.query(TrainingDataset).count()
    if dataset_count == 0:
        raise HTTPException(status_code=400, detail="No verified training data available yet")

    job = RetrainingQueue(
        triggered_by=token_payload["sub"],
        status="queued",
        dataset_snapshot_count=dataset_count,
        notes="Triggered manually via dashboard",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/retrain/queue", response_model=list[RetrainingQueueOut])
def list_retraining_jobs(db: Session = Depends(get_db), _user=Depends(require_roles("administrator", "supervisor"))):
    return db.query(RetrainingQueue).order_by(RetrainingQueue.created_at.desc()).all()
