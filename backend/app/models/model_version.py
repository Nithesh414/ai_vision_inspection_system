from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime

from app.db.session import Base


class ModelVersion(Base):

    __tablename__ = "model_versions"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    model_name = Column(
        String,
        default="Industrial_AI_Model"
    )


    version = Column(
        String,
        default="v1.0"
    )


    accuracy = Column(
        Float,
        default=0
    )


    loss = Column(
        Float,
        default=0
    )


    path = Column(
        String,
        nullable=True
    )


    active = Column(
        Boolean,
        default=False
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
