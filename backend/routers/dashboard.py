from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from core.database import get_db
from core.security import get_current_user
from models.models import Product, Transaction, TransactionType, DepartmentEnum, User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
def get_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = date.today()
    total_products = db.query(Product).count()
    total_stock_value = db.query(func.sum(Product.price * Product.quantity)).scalar() or 0
    low_stock_count = db.query(Product).filter(Product.quantity <= Product.low_stock_threshold).count()

    today_sales = db.query(func.sum(Transaction.total_amount)).filter(
        Transaction.transaction_type == TransactionType.sale,
        func.date(Transaction.created_at) == today
    ).scalar() or 0

    today_purchases = db.query(func.sum(Transaction.total_amount)).filter(
        Transaction.transaction_type == TransactionType.purchase,
        func.date(Transaction.created_at) == today
    ).scalar() or 0

    dept_counts = {}
    for dept in DepartmentEnum:
        count = db.query(Product).filter(Product.department == dept).count()
        dept_counts[dept.value] = count

    recent_transactions = db.query(Transaction).order_by(
        Transaction.created_at.desc()
    ).limit(10).all()

    recent = []
    for t in recent_transactions:
        product = db.query(Product).filter(Product.id == t.product_id).first()
        recent.append({
            "id": t.id,
            "product_name": product.name if product else "Unknown",
            "product_code": product.code if product else "",
            "transaction_type": t.transaction_type.value,
            "quantity": t.quantity,
            "total_amount": t.total_amount,
            "created_at": t.created_at.isoformat()
        })

    return {
        "total_products": total_products,
        "total_stock_value": round(total_stock_value, 2),
        "low_stock_count": low_stock_count,
        "today_sales": round(today_sales, 2),
        "today_purchases": round(today_purchases, 2),
        "department_counts": dept_counts,
        "recent_transactions": recent
    }
