from sqlalchemy import Column, String, Boolean, Integer, Text, ForeignKey, SmallInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy import TIMESTAMP
from app.core.database import Base
import uuid

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_no = Column(String(12), unique=True, nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    total_price = Column(Integer, nullable=False)
    points_earned = Column(Integer, nullable=False, default=0)
    note = Column(Text, nullable=True)
    confirmed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    ready_at = Column(TIMESTAMP(timezone=True), nullable=True)
    completed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_name = Column(String(100), nullable=False)
    size = Column(String(5), nullable=False)
    sugar = Column(String(10), nullable=False)
    ice = Column(String(20), nullable=False)
    extras = Column(JSONB, nullable=False, default=list)
    quantity = Column(SmallInteger, nullable=False)
    unit_price = Column(Integer, nullable=False)
    subtotal = Column(Integer, nullable=False)
