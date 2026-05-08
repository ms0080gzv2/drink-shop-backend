from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, menu, members, orders, webhook, reports

app = FastAPI(title="手搖飲料店會員點餐系統", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(members.router)
app.include_router(orders.router)
app.include_router(webhook.router)
app.include_router(reports.router)

@app.get("/")
async def root():
    return {"message": "手搖飲料店 API 運行中 🧋"}

@app.get("/health")
async def health():
    return {"status": "ok"}
