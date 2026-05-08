from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.models.member import Member
from app.models.admin_user import AdminUser
from sqlalchemy import select
import uuid

security = HTTPBearer()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token 無效或已過期")

async def get_current_member(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    payload = decode_token(credentials.credentials)
    if payload.get("role") != "member":
        raise HTTPException(status_code=403, detail="權限不足")
    member = await db.get(Member, uuid.UUID(payload["sub"]))
    if not member or not member.is_active:
        raise HTTPException(status_code=401, detail="會員不存在或已停用")
    return member

async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    payload = decode_token(credentials.credentials)
    if payload.get("role") not in ("admin", "owner", "staff"):
        raise HTTPException(status_code=403, detail="需要管理員權限")
    admin = await db.get(AdminUser, uuid.UUID(payload["sub"]))
    if not admin or not admin.is_active:
        raise HTTPException(status_code=401, detail="管理員不存在或已停用")
    return admin
