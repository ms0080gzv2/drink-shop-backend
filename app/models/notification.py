from sqlalchemy import Column, String, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import TIMESTAMP
from app.core.database import Base
import uuid

class MemberNotification(Base):
    __tablename__ = "member_notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True)
    type = Column(String(30), nullable=False)
    message = Column(Text, nullable=False)
    sent_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    is_success = Column(Boolean, nullable=False, default=True)
    error_msg = Column(Text, nullable=True)
