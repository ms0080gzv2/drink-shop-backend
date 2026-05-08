from sqlalchemy import Column, String, Boolean, Integer, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy import TIMESTAMP
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price_m = Column(Integer, nullable=False)
    price_l = Column(Integer, nullable=True)
    image_url = Column(Text, nullable=True)
    is_available = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)
    allow_hot = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class ProductExtra(Base):
    __tablename__ = "product_extras"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    price = Column(Integer, nullable=False, default=0)
    is_available = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)
