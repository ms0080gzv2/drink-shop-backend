from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.dependencies import get_db, get_current_member, get_current_admin
from app.models.member import Member
from app.models.point_log import PointLog

router = APIRouter(prefix="/api/members", tags=["會員"])

@router.get("/me")
async def get_me(member=Depends(get_current_member)):
    return {"success": True, "data": {
        "id": str(member.id),
        "display_name": member.display_name,
        "picture_url": member.picture_url,
        "phone": member.phone,
        "birthday": str(member.birthday) if member.birthday else None,
        "points": member.points,
        "total_spent": member.total_spent,
    }}

class MemberUpdate(BaseModel):
    phone: Optional[str] = None
    birthday: Optional[date] = None

@router.patch("/me")
async def update_me(body: MemberUpdate, db: AsyncSession = Depends(get_db), member=Depends(get_current_member)):
    if body.phone:
        member.phone = body.phone
    if body.birthday and member.birthday is None:
        member.birthday = body.birthday
    elif body.birthday and member.birthday is not None:
        raise HTTPException(status_code=400, detail="生日設定後不可更改")
    await db.commit()
    return {"success": True, "message": "更新成功"}

@router.get("/me/points")
async def get_my_points(db: AsyncSession = Depends(get_db), member=Depends(get_current_member)):
    result = await db.execute(
        select(PointLog).where(PointLog.member_id == member.id).order_by(PointLog.created_at.desc()).limit(50)
    )
    logs = result.scalars().all()
    return {"success": True, "data": [
        {"delta": l.delta, "balance_after": l.balance_after, "type": l.type, "note": l.note, "created_at": str(l.created_at)}
        for l in logs
    ]}

@router.get("")
async def get_all_members(db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    result = await db.execute(select(Member).order_by(Member.created_at.desc()))
    members = result.scalars().all()
    return {"success": True, "data": [
        {"id": str(m.id), "display_name": m.display_name, "phone": m.phone,
         "points": m.points, "total_spent": m.total_spent, "is_active": m.is_active}
        for m in members
    ]}
