"""
Optional convenience script: creates a demo administrator account and a
sample product specification so you can exercise the API immediately
after first deploy. Run once:

    python seed.py

Equivalent to calling POST /api/auth/bootstrap-admin + POST /api/products
by hand.
"""
from app.db.session import SessionLocal, Base, engine
from app.models.models import User, Product
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    if db.query(User).count() == 0:
        admin = User(
            username="admin",
            full_name="System Administrator",
            email="admin@example.com",
            hashed_password=hash_password("ChangeMe123!"),
            role="administrator",
        )
        db.add(admin)
        print("Created administrator account -> username: admin / password: ChangeMe123!  (CHANGE THIS)")
    else:
        print("Users already exist — skipping admin creation.")

    if db.query(Product).filter(Product.code == "DEMO-001").first() is None:
        demo_product = Product(
            name="Demo Valve Assembly",
            code="DEMO-001",
            description="Sample product spec for testing the inspection pipeline.",
            specification={
                "components": {"bolt": 8, "valve": 1, "cover": 1},
                "position_tolerance_px": 15,
                "critical_defect_types": ["crack", "broken_component", "missing_component"],
                "major_defect_types": ["dent", "rust", "misalignment", "surface_damage"],
                "minor_defect_types": ["scratch"],
            },
        )
        db.add(demo_product)
        print("Created demo product: DEMO-001 — Demo Valve Assembly")
    else:
        print("Demo product already exists — skipping.")

    db.commit()
finally:
    db.close()
