from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import Inspection, Defect, InspectionStatus
from app.schemas.schemas import DashboardSummary
from app.core.security import get_token_payload

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db), _payload=Depends(get_token_payload)):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    todays_inspections = db.query(Inspection).filter(Inspection.created_at >= today_start).count()
    pass_count = db.query(Inspection).filter(
        Inspection.created_at >= today_start, Inspection.status == InspectionStatus.PASS_
    ).count()
    fail_count = db.query(Inspection).filter(
        Inspection.created_at >= today_start, Inspection.status == InspectionStatus.FAIL
    ).count()

    defect_counts = (
        db.query(Defect.defect_type, func.count(Defect.id).label("count"))
        .group_by(Defect.defect_type)
        .order_by(func.count(Defect.id).desc())
        .limit(5)
        .all()
    )

    accuracy = round(pass_count / todays_inspections, 4) if todays_inspections else None

    return DashboardSummary(
        todays_inspections=todays_inspections,
        pass_count=pass_count,
        fail_count=fail_count,
        accuracy_estimate=accuracy,
        most_common_defects=[{"defect_type": dt, "count": c} for dt, c in defect_counts],
    )


@router.get("/trends")
def inspection_trends(days: int = 30, db: Session = Depends(get_db), _payload=Depends(get_token_payload)):
    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(
            func.date(Inspection.created_at).label("day"),
            Inspection.status,
            func.count(Inspection.id).label("count"),
        )
        .filter(Inspection.created_at >= since)
        .group_by(func.date(Inspection.created_at), Inspection.status)
        .order_by(func.date(Inspection.created_at))
        .all()
    )
    return [{"day": str(r.day), "status": r.status.value, "count": r.count} for r in rows]
