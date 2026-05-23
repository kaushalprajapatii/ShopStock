from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO
from core.database import get_db
from core.security import get_current_user
from models.models import Product, Transaction, User
import openpyxl
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/products/excel")
def export_products_excel(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    products = db.query(Product).order_by(Product.department, Product.name).all()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Products"
    headers = ["Code", "Name", "Department", "Quantity", "Price (₹)", "Stock Value (₹)", "Low Stock Threshold", "Status"]
    ws.append(headers)
    for p in products:
        status = "LOW STOCK" if p.quantity <= p.low_stock_threshold else "OK"
        ws.append([p.code, p.name, p.department.value, p.quantity, p.price, round(p.quantity * p.price, 2), p.low_stock_threshold, status])
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=products_{datetime.now().strftime('%Y%m%d')}.xlsx"})

@router.get("/products/pdf")
def export_products_pdf(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    products = db.query(Product).order_by(Product.department, Product.name).all()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    elements = [Paragraph("Products Report", styles['Title']), Spacer(1, 12)]
    data = [["Code", "Name", "Department", "Qty", "Price (₹)", "Value (₹)", "Status"]]
    for p in products:
        status = "LOW" if p.quantity <= p.low_stock_threshold else "OK"
        data.append([p.code, p.name, p.department.value, str(p.quantity), f"₹{p.price:.2f}", f"₹{p.quantity*p.price:.2f}", status])
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=products_{datetime.now().strftime('%Y%m%d')}.pdf"})

@router.get("/transactions/excel")
def export_transactions_excel(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).order_by(Transaction.created_at.desc()).all()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Transactions"
    ws.append(["ID", "Product Code", "Product Name", "Department", "Type", "Quantity", "Price/Unit (₹)", "Total (₹)", "Note", "Date"])
    for t in transactions:
        ws.append([t.id, t.product.code, t.product.name, t.product.department.value,
                   t.transaction_type.value.upper(), t.quantity, t.price_per_unit,
                   t.total_amount, t.note or "", t.created_at.strftime("%Y-%m-%d %H:%M")])
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=transactions_{datetime.now().strftime('%Y%m%d')}.xlsx"})

@router.get("/transactions/pdf")
def export_transactions_pdf(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).order_by(Transaction.created_at.desc()).limit(200).all()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    elements = [Paragraph("Transactions Report", styles['Title']), Spacer(1, 12)]
    data = [["Product", "Department", "Type", "Qty", "Price (₹)", "Total (₹)", "Date"]]
    for t in transactions:
        data.append([t.product.name, t.product.department.value, t.transaction_type.value.upper(),
                     str(t.quantity), f"₹{t.price_per_unit:.2f}", f"₹{t.total_amount:.2f}",
                     t.created_at.strftime("%Y-%m-%d %H:%M")])
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=transactions_{datetime.now().strftime('%Y%m%d')}.pdf"})
