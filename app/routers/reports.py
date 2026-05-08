from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Date
from datetime import datetime, timezone, timedelta
from app.dependencies import get_db, get_current_admin
from app.models.order import Order

router = APIRouter(prefix="/api/reports", tags=["報表"])

@router.get("/summary")
async def get_summary(db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    """今日、本週、本月統計"""
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    async def get_stats(since):
        result = await db.execute(
            select(
                func.count(Order.id).label("count"),
                func.coalesce(func.sum(Order.total_price), 0).label("revenue")
            ).where(Order.created_at >= since, Order.status != "cancelled")
        )
        return result.one()

    today_stats = await get_stats(today)
    week_stats = await get_stats(week_start)
    month_stats = await get_stats(month_start)

    # 各狀態訂單數
    status_result = await db.execute(
        select(Order.status, func.count(Order.id)).group_by(Order.status)
    )
    status_counts = {row[0]: row[1] for row in status_result.all()}

    return {"success": True, "data": {
        "today": {"orders": today_stats.count, "revenue": int(today_stats.revenue)},
        "week": {"orders": week_stats.count, "revenue": int(week_stats.revenue)},
        "month": {"orders": month_stats.count, "revenue": int(month_stats.revenue)},
        "status_counts": status_counts,
    }}

@router.get("/daily")
async def get_daily(days: int = 14, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    """最近 N 天每日營業額"""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(
            cast(Order.created_at, Date).label("date"),
            func.count(Order.id).label("orders"),
            func.coalesce(func.sum(Order.total_price), 0).label("revenue")
        ).where(
            Order.created_at >= since,
            Order.status != "cancelled"
        ).group_by(cast(Order.created_at, Date))
        .order_by(cast(Order.created_at, Date))
    )
    rows = result.all()
    return {"success": True, "data": [
        {"date": str(r.date), "orders": r.orders, "revenue": int(r.revenue)}
        for r in rows
    ]}
