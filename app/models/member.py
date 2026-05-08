from sqlalchemy import Column, String, Boolean, Integer, Date, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import TIMESTAMP
from app.core.database import Base
import uuid

class Member(Base):
    __tablename__ = "members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    line_user_id = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    picture_url = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    birthday = Column(Date, nullable=True)
    points = Column(Integer, nullable=False, default=0)
    total_spent = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
