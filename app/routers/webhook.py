from fastapi import APIRouter, Request, HTTPException, Header
from app.core.config import settings
import hashlib, hmac, base64, json

router = APIRouter(prefix="/api/webhook", tags=["Webhook"])

def verify_signature(body: bytes, signature: str) -> bool:
    channel_secret = settings.line_channel_secret.encode("utf-8")
    hash = hmac.new(channel_secret, body, hashlib.sha256).digest()
    expected = base64.b64encode(hash).decode("utf-8")
    return hmac.compare_digest(expected, signature)

@router.post("/line")
async def line_webhook(
    request: Request,
    x_line_signature: str = Header(None)
):
    body = await request.body()
    if not x_line_signature or not verify_signature(body, x_line_signature):
        raise HTTPException(status_code=400, detail="Invalid signature")
    data = json.loads(body)
    print(f"LINE Webhook received: {data}")
    return {"status": "ok"}
