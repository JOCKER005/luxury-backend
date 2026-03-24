from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone


def utcnow():
    return datetime.now(timezone.utc)


class Product(Base):
    __tablename__ = "products"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(200), nullable=False)
    category    = Column(String(50), nullable=False)
    price       = Column(Float, nullable=False)
    stock       = Column(Integer, default=0)
    featured    = Column(Boolean, default=False)
    active      = Column(Boolean, default=True)
    rating      = Column(Float, default=5.0)
    reviews     = Column(Integer, default=0)
    description = Column(Text, default="")
    image       = Column(String(500), default="")
    # Campo nuevo: JSON con lista de URLs adicionales de imágenes
    # Se guarda como texto JSON: '["url1","url2","url3"]'
    images      = Column(Text, default="[]")
    created_at  = Column(DateTime(timezone=True), default=utcnow)
    updated_at  = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id                = Column(Integer, primary_key=True, index=True)
    mp_preference_id  = Column(String(200), index=True, nullable=True)
    mp_payment_id     = Column(String(200), nullable=True)
    status            = Column(String(50), default="pending")
    total             = Column(Float, default=0)
    created_at        = Column(DateTime(timezone=True), default=utcnow)
    updated_at        = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id           = Column(Integer, primary_key=True, index=True)
    order_id     = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id   = Column(Integer, ForeignKey("products.id"), nullable=True)
    product_name = Column(String(200), nullable=False)
    quantity     = Column(Integer, default=1)
    unit_price   = Column(Float, default=0)

    order   = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
