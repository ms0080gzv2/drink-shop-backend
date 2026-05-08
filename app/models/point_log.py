from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import TIMESTAMP
from app.core.database import Base
import uuid

class PointLog(Base):
    __tablename__ = "point_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True)
    delta = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    type = Column(String(20), nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=True)
