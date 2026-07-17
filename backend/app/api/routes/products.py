from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import Product
from app.schemas.schemas import ProductCreate, ProductOut
from app.core.security import require_roles, get_token_payload

router = APIRouter(prefix="/api/products", tags=["products"])


@router.post("", response_model=ProductOut, status_code=201)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("administrator", "supervisor")),
):
    existing = db.query(Product).filter(Product.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product code already exists")

    product = Product(
        name=payload.name,
        code=payload.code,
        description=payload.description,
        specification=payload.specification,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db), _payload=Depends(get_token_payload)):
    return db.query(Product).order_by(Product.created_at.desc()).all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: str, db: Session = Depends(get_db), _payload=Depends(get_token_payload)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: str,
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("administrator", "supervisor")),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.name = payload.name
    product.description = payload.description
    product.specification = payload.specification
    db.commit()
    db.refresh(product)
    return product
