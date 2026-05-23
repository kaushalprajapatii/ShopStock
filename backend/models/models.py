from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from core.database import Base


class DepartmentEnum(str, enum.Enum):
    stationery = "Stationery"
    gifts = "Gifts"
    furniture = "Furniture"
    sports = "Sports"
    daily_items = "Daily Items"
    


class TransactionType(str, enum.Enum):
    sale = "sale"
    purchase = "purchase"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    department = Column(Enum(DepartmentEnum), nullable=False)
    quantity = Column(Integer, default=0)
    price = Column(Float, nullable=False)
    low_stock_threshold = Column(Integer, default=10)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    transactions = relationship("Transaction", back_populates="product")


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    product = relationship("Product", back_populates="transactions")
