"""
SQLAlchemy ORM models for all tables described in the project spec:
Users, Products, Inspection, Defects, Inspection Reports, Training Dataset,
Retraining Queue, Model Versions, Supervisor Feedback.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


def gen_uuid():
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"
    ADMINISTRATOR = "administrator"


class InspectionStatus(str, enum.Enum):
    PASS_ = "PASS"
    FAIL = "FAIL"
    PENDING = "PENDING"


class Severity(str, enum.Enum):
    NONE = "none"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class VerificationStatus(str, enum.Enum):
    UNVERIFIED = "unverified"
    VERIFIED_CORRECT = "verified_correct"
    VERIFIED_CORRECTED = "verified_corrected"
    REJECTED = "rejected"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    username = Column(String(64), unique=True, nullable=False, index=True)
    full_name = Column(String(128), nullable=True)
    email = Column(String(128), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.OPERATOR)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    inspections = relationship("Inspection", back_populates="operator", foreign_keys="Inspection.operator_id")


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String(128), nullable=False)
    code = Column(String(64), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    # Specification stored as JSON, e.g.
    # {"components": {"bolt": 8, "valve": 1, "cover": 1}, "tolerances": {...}}
    specification = Column(JSON, nullable=False, default=dict)
    active_model_version_id = Column(UUID(as_uuid=False), ForeignKey("model_versions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    inspections = relationship("Inspection", back_populates="product")


class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    product_id = Column(UUID(as_uuid=False), ForeignKey("products.id"), nullable=False)
    operator_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)

    image_path = Column(String(512), nullable=False)
    status = Column(Enum(InspectionStatus), nullable=False, default=InspectionStatus.PENDING)
    confidence = Column(Float, nullable=True)
    severity = Column(Enum(Severity), nullable=True)

    ai_raw_output = Column(JSON, nullable=True)   # raw detections from AI modules
    rule_engine_output = Column(JSON, nullable=True)  # rule evaluation trace

    inspection_time_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="inspections")
    operator = relationship("User", back_populates="inspections", foreign_keys=[operator_id])
    defects = relationship("Defect", back_populates="inspection", cascade="all, delete-orphan")
    report = relationship("InspectionReport", back_populates="inspection", uselist=False, cascade="all, delete-orphan")
    feedback = relationship("SupervisorFeedback", back_populates="inspection", cascade="all, delete-orphan")


class Defect(Base):
    __tablename__ = "defects"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    inspection_id = Column(UUID(as_uuid=False), ForeignKey("inspections.id"), nullable=False)

    defect_type = Column(String(64), nullable=False)  # scratch, crack, dent, rust, missing_component, etc.
    component_name = Column(String(64), nullable=True)  # e.g. "Top Right Bolt"
    location = Column(JSON, nullable=True)  # bounding box {x, y, w, h}
    severity = Column(Enum(Severity), nullable=False, default=Severity.MINOR)
    confidence = Column(Float, nullable=True)
    suggested_correction = Column(String(255), nullable=True)

    inspection = relationship("Inspection", back_populates="defects")


class InspectionReport(Base):
    __tablename__ = "inspection_reports"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    inspection_id = Column(UUID(as_uuid=False), ForeignKey("inspections.id"), unique=True, nullable=False)
    pdf_path = Column(String(512), nullable=True)
    summary = Column(Text, nullable=True)
    reasons = Column(JSON, nullable=True)  # list of reason strings
    suggested_actions = Column(JSON, nullable=True)  # list of action strings
    generated_at = Column(DateTime, default=datetime.utcnow)

    inspection = relationship("Inspection", back_populates="report")


class TrainingDataset(Base):
    __tablename__ = "training_dataset"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    inspection_id = Column(UUID(as_uuid=False), ForeignKey("inspections.id"), nullable=True)
    image_path = Column(String(512), nullable=False)
    label = Column(String(64), nullable=False)  # good, missing_component, misaligned, crack, scratch...
    split = Column(String(16), default="train")  # train / validation / test
    added_at = Column(DateTime, default=datetime.utcnow)


class RetrainingQueue(Base):
    __tablename__ = "retraining_queue"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    triggered_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    status = Column(String(32), default="queued")  # queued, running, completed, failed
    dataset_snapshot_count = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    module = Column(String(32), nullable=False)  # product_detection, component_detection, defect_detection
    version_tag = Column(String(32), nullable=False)  # e.g. v1.0.3
    weights_path = Column(String(512), nullable=False)
    metrics = Column(JSON, nullable=True)  # {"precision":.., "recall":.., "map50":..}
    is_active = Column(Boolean, default=False)
    trained_at = Column(DateTime, default=datetime.utcnow)


class SupervisorFeedback(Base):
    __tablename__ = "supervisor_feedback"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    inspection_id = Column(UUID(as_uuid=False), ForeignKey("inspections.id"), nullable=False)
    supervisor_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    verification_status = Column(Enum(VerificationStatus), nullable=False, default=VerificationStatus.UNVERIFIED)
    corrected_label = Column(String(64), nullable=True)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    inspection = relationship("Inspection", back_populates="feedback")
