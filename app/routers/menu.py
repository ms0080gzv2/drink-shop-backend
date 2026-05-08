from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.dependencies import get_db, get_current_admin
from app.models.category import Category
from app.models.product import Product, ProductExtra

router = APIRouter(prefix="/api/menu", tags=["菜單"])

# ── 分類 ──────────────────────────────────────
@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.is_active == True).order_by(Category.sort_order))
    categories = result.scalars().all()
    return {"success": True, "data": [
        {"id": c.id, "name": c.name, "sort_order": c.sort_order} for c in categories
    ]}

class CategoryCreate(BaseModel):
    name: str
    sort_order: int = 0

@router.post("/categories")
async def create_category(body: CategoryCreate, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    cat = Category(name=body.name, sort_order=body.sort_order)
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return {"success": True, "data": {"id": cat.id, "name": cat.name}}

# ── 商品 ──────────────────────────────────────
@router.get("/products")
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.is_available == True).order_by(Product.category_id, Product.sort_order))
    products = result.scalars().all()
    return {"success": True, "data": [
        {
            "id": p.id, "category_id": p.category_id, "name": p.name,
            "description": p.description, "price_m": p.price_m, "price_l": p.price_l,
            "image_url": p.image_url, "is_available": p.is_available, "allow_hot": p.allow_hot
        } for p in products
    ]}

class ProductCreate(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None
    price_m: int
    price_l: Optional[int] = None
    allow_hot: bool = False
    sort_order: int = 0

@router.post("/products")
async def create_product(body: ProductCreate, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    product = Product(**body.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return {"success": True, "data": {"id": product.id, "name": product.name}}

@router.patch("/products/{id}")
async def update_product(id: int, body: ProductCreate, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    product = await db.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    for k, v in body.model_dump().items():
        setattr(product, k, v)
    await db.commit()
    return {"success": True, "message": "更新成功"}

@router.delete("/products/{id}")
async def delete_product(id: int, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    product = await db.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    product.is_available = False
    await db.commit()
    return {"success": True, "message": "已下架"}

# ── 加料 ──────────────────────────────────────
@router.get("/extras")
async def get_extras(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductExtra).where(ProductExtra.is_available == True).order_by(ProductExtra.sort_order))
    extras = result.scalars().all()
    return {"success": True, "data": [
        {"id": e.id, "name": e.name, "price": e.price} for e in extras
    ]}
