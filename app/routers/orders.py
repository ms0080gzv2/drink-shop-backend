from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from app.dependencies import get_db, get_current_member, get_current_admin
from app.models.order import Order, OrderItem
from app.models.member import Member
import uuid

router = APIRouter(prefix="/api/orders", tags=["訂單"])

class OrderItemCreate(BaseModel):
    product_id: int
    product_name: str
    size: str
    sugar: str
    ice: str
    extras: List[dict] = []
    quantity: int
    unit_price: int
    subtotal: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    note: Optional[str] = None

def gen_order_no() -> str:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"{today}-{str(uuid.uuid4())[:4].upper()}"

@router.post("")
async def create_order(body: OrderCreate, db: AsyncSession = Depends(get_db), member=Depends(get_current_member)):
    total = sum(i.subtotal * i.quantity for i in body.items)
    points_earned = total // 10  # 每消費 10 元獲得 1 點

    order = Order(
        id=uuid.uuid4(),
        order_no=gen_order_no(),
        member_id=member.id,
        status="pending",
        total_price=total,
        points_earned=points_earned,
        note=body.note,
    )
    db.add(order)
    await db.flush()

    for item in body.items:
        db.add(OrderItem(
            id=uuid.uuid4(),
            order_id=order.id,
            **item.model_dump()
        ))

    member.points += points_earned
    member.total_spent += total
    await db.commit()
    return {"success": True, "data": {"order_id": str(order.id), "order_no": order.order_no, "points_earned": points_earned}}

@router.get("/my")
async def get_my_orders(db: AsyncSession = Depends(get_db), member=Depends(get_current_member)):
    since = datetime.now(timezone.utc) - timedelta(days=30)
    result = await db.execute(
        select(Order).where(Order.member_id == member.id, Order.created_at >= since).order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()
    return {"success": True, "data": [
        {"id": str(o.id), "order_no": o.order_no, "status": o.status,
         "total_price": o.total_price, "created_at": str(o.created_at)}
        for o in orders
    ]}

@router.get("")
async def get_all_orders(db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    result = await db.execute(select(Order).order_by(Order.created_at.desc()).limit(100))
    orders = result.scalars().all()
    return {"success": True, "data": [
        {"id": str(o.id), "order_no": o.order_no, "status": o.status,
         "total_price": o.total_price, "created_at": str(o.created_at)}
        for o in orders
    ]}

class StatusUpdate(BaseModel):
    status: str

@router.patch("/{id}/status")
async def update_order_status(id: str, body: StatusUpdate, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    order = await db.get(Order, uuid.UUID(id))
    if not order:
        raise HTTPException(status_code=404, detail="訂單不存在")
    allowed = {"pending": ["confirmed", "cancelled"], "confirmed": ["ready", "cancelled"], "ready": ["completed"]}
    if body.status not in allowed.get(order.status, []):
        raise HTTPException(status_code=400, detail=f"無法從 {order.status} 轉換至 {body.status}")
    order.status = body.status
    now = datetime.now(timezone.utc)
    if body.status == "confirmed": order.confirmed_at = now
    elif body.status == "ready": order.ready_at = now
    elif body.status == "completed": order.completed_at = now
    await db.commit()
    return {"success": True, "message": "訂單狀態已更新"}
