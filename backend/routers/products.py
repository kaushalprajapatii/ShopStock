from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.security import get_current_user
from models.models import Product, DepartmentEnum, User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/products", tags=["products"])

class ProductCreate(BaseModel):
    name: str
    code: str
    department: DepartmentEnum
    quantity: int = 0
    price: float
    low_stock_threshold: int = 10
    description: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[DepartmentEnum] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    low_stock_threshold: Optional[int] = None
    description: Optional[str] = None

class ProductOut(BaseModel):
    id: int
    name: str
    code: str
    department: DepartmentEnum
    quantity: int
    price: float
    low_stock_threshold: int
    description: Optional[str]
    created_at: datetime
    is_low_stock: bool = False

    class Config:
        from_attributes = True

@router.get("/", response_model=List[ProductOut])
def get_products(
    department: Optional[DepartmentEnum] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Product)
    if department:
        query = query.filter(Product.department == department)
    if search:
        query = query.filter(
            (Product.name.ilike(f"%{search}%")) | (Product.code.ilike(f"%{search}%"))
        )
    products = query.order_by(Product.name).all()
    result = []
    for p in products:
        d = ProductOut.model_validate(p)
        d.is_low_stock = p.quantity <= p.low_stock_threshold
        result.append(d)
    return result

@router.get("/low-stock", response_model=List[ProductOut])
def get_low_stock(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    products = db.query(Product).filter(Product.quantity <= Product.low_stock_threshold).all()
    result = []
    for p in products:
        d = ProductOut.model_validate(p)
        d.is_low_stock = True
        result.append(d)
    return result

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    d = ProductOut.model_validate(p)
    d.is_low_stock = p.quantity <= p.low_stock_threshold
    return d

@router.post("/", response_model=ProductOut, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(Product).filter(Product.code == data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product code already exists")
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    d = ProductOut.model_validate(product)
    d.is_low_stock = product.quantity <= product.low_stock_threshold
    return d

@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    d = ProductOut.model_validate(product)
    d.is_low_stock = product.quantity <= product.low_stock_threshold
    return d

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}
