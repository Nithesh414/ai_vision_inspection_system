"""
Pydantic request/response schemas.
"""
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- Auth ----------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class LoginRequest(BaseModel):
    username: str
    password: str


# ---------- Users ----------
class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: str = "operator"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime


# ---------- Products ----------
class ProductCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    specification: dict  # e.g. {"components": {"bolt": 8, "valve": 1}, "tolerances": {}}


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    code: str
    description: Optional[str] = None
    specification: dict
    created_at: datetime


# ---------- Defects ----------
class DefectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    defect_type: str
    component_name: Optional[str] = None
    location: Optional[dict] = None
    severity: str
    confidence: Optional[float] = None
    suggested_correction: Optional[str] = None


# ---------- Inspections ----------
class InspectionCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    product_id: str
    status: str
    confidence: Optional[float] = None
    severity: Optional[str] = None
    inspection_time_seconds: Optional[float] = None
    created_at: datetime
    defects: list[DefectOut] = []
    reasons: list[str] = []
    suggested_actions: list[str] = []


class InspectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    product_id: str
    operator_id: str
    image_path: str
    status: str
    confidence: Optional[float] = None
    severity: Optional[str] = None
    inspection_time_seconds: Optional[float] = None
    created_at: datetime
    defects: list[DefectOut] = []


# ---------- Supervisor Feedback ----------
class SupervisorFeedbackCreate(BaseModel):
    verification_status: str  # verified_correct, verified_corrected, rejected
    corrected_label: Optional[str] = None
    comments: Optional[str] = None


class SupervisorFeedbackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    inspection_id: str
    supervisor_id: str
    verification_status: str
    corrected_label: Optional[str] = None
    comments: Optional[str] = None
    created_at: datetime


# ---------- Analytics ----------
class DashboardSummary(BaseModel):
    todays_inspections: int
    pass_count: int
    fail_count: int
    accuracy_estimate: Optional[float] = None
    most_common_defects: list[dict[str, Any]]  # [{"defect_type": "scratch", "count": 12}]


# ---------- Model Versions ----------
class ModelVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    module: str
    version_tag: str
    weights_path: str
    metrics: Optional[dict] = None
    is_active: bool
    trained_at: datetime


class RetrainingQueueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    status: str
    dataset_snapshot_count: int
    notes: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
