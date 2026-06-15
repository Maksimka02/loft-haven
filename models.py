from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    material = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    specifications = Column(Text)
    images = Column(Text)
    in_stock = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    cart_items = relationship("CartItem", back_populates="product")
    comparison_items = relationship("ComparisonItem", back_populates="product")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="cart_items")

class ComparisonItem(Base):
    __tablename__ = "comparison_items"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    added_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="comparison_items")

class ConsultationRequest(Base):
    __tablename__ = "consultation_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    product_name = Column(String(200))
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_processed = Column(Boolean, default=False)