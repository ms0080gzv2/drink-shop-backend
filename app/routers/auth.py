from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from app.dependencies import get_db, get_current_member
from app.core.config import settings
from app.models.member import Member
from app.models.admin_user import AdminUser
import httpx, uuid, bcrypt

router = APIRouter(prefix="/api/auth", tags=["認證"])

def create_token(sub: str, role: str, expire_minutes: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    return jwt.encode({"sub": sub, "role": role, "exp": expire}, settings.secret_key, algorithm=settings.algorithm)

class LineLoginRequest(BaseModel):
    id_token: str

class AdminLoginRequest(BaseModel):
    email: str
    password: str

@router.post("/line-login")
async def line_login(body: LineLoginRequest, db: AsyncSession = Depends(get_db)):
    # 向 LINE 驗證 id_token
    async with httpx.AsyncClient() as client:
        resp = await client.post("https://api.line.me/oauth2/v2.1/verify", data={
            "id_token": body.id_token,
            "client_id": settings.line_login_channel_id,
        })
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="LINE Token 驗證失敗")
    line_data = resp.json()

    # 查找或建立會員
    result = await db.execute(select(Member).where(Member.line_user_id == line_data["sub"]))
    member = result.scalar_one_or_none()
    if not member:
        member = Member(
            id=uuid.uuid4(),
            line_user_id=line_data["sub"],
            display_name=line_data.get("name", ""),
            picture_url=line_data.get("picture", None),
        )
        db.add(member)
        await db.commit()
        await db.refresh(member)

    token = create_token(str(member.id), "member", settings.access_token_expire_minutes)
    return {"success": True, "access_token": token, "token_type": "bearer"}

@router.post("/admin-login")
async def admin_login(body: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AdminUser).where(AdminUser.email == body.email))
    admin = result.scalar_one_or_none()
    if not admin or not bcrypt.checkpw(body.password.encode(), admin.password_hash.encode()):
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    if not admin.is_active:
        raise HTTPException(status_code=403, detail="帳號已停用")
    admin.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    token = create_token(str(admin.id), "admin", 1440)
    return {"success": True, "access_token": token, "token_type": "bearer"}

@router.post("/logout")
async def logout(member=Depends(get_current_member)):
    return {"success": True, "message": "已登出"}
