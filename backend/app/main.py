"""
AI-Powered Intelligent Product Inspection System — FastAPI entrypoint.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import wheel_inspection

from app.core.config import settings
from app.db.session import Base, engine
from app.api.routes import auth, products, inspections, analytics, models_admin

# Create tables (for local/dev; use Alembic migrations in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Industrial AI quality inspection platform: product/component/defect "
                "detection, rule-based PASS/FAIL decisions, and continuous learning.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(inspections.router)
app.include_router(analytics.router)
app.include_router(models_admin.router)

app.include_router(wheel_inspection.router)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
