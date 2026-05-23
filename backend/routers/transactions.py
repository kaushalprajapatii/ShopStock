from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from core.database import get_db
from core.security import get_current_user
from models.models import Transaction, Product, TransactionType, DepartmentEnum, User
from pydantic import BaseModel
from datetime import datetime, date

router = APIRouter(prefix="/transactions", tags=["transactions"])

class TransactionCreate(BaseModel):
    product_id: int
    transaction_type: TransactionType
    quantity: int
    price_per_unit: float
    note: Optional[str] = None

class TransactionOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_code: str
    department: str
    transaction_type: TransactionType
    quantity: int
    price_per_unit: float
    total_amount: float
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[TransactionOut])
def get_transactions(
    transaction_type: Optional[TransactionType] = None,
    department: Optional[DepartmentEnum] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Transaction).options(joinedload(Transaction.product))
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)
    if department:
        query = query.join(Product).filter(Product.department == department)
    if date_from:
        query = query.filter(Transaction.created_at >= date_from)
    if date_to:
        from datetime import timedelta
        query = query.filter(Transaction.created_at < date_to + timedelta(days=1))
    transactions = query.order_by(Transaction.created_at.desc()).limit(limit).all()
    result = []
    for t in transactions:
        result.append(TransactionOut(
            id=t.id,
            product_id=t.product_id,
            product_name=t.product.name,
            product_code=t.product.code,
            department=t.product.department.value,
            transaction_type=t.transaction_type,
            quantity=t.quantity,
            price_per_unit=t.price_per_unit,
            total_amount=t.total_amount,
            note=t.note,
            created_at=t.created_at
        ))
    return result

@router.post("/", response_model=TransactionOut, status_code=201)
def create_transaction(data: TransactionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if data.transaction_type == TransactionType.sale:
        if product.quantity < data.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock. Available: {product.quantity}")
        product.quantity -= data.quantity
    else:
        product.quantity += data.quantity
    total = data.quantity * data.price_per_unit
    transaction = Transaction(
        product_id=data.product_id,
        transaction_type=data.transaction_type,
        quantity=data.quantity,
        price_per_unit=data.price_per_unit,
        total_amount=total,
        note=data.note
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    db.refresh(product)
    return TransactionOut(
        id=transaction.id,
        product_id=transaction.product_id,
        product_name=product.name,
        product_code=product.code,
        department=product.department.value,
        transaction_type=transaction.transaction_type,
        quantity=transaction.quantity,
        price_per_unit=transaction.price_per_unit,
        total_amount=transaction.total_amount,
        note=transaction.note,
        created_at=transaction.created_at
    )
