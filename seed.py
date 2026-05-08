import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal, engine, Base
from app.models.admin_user import AdminUser
from app.models.category import Category
from app.models.product import Product, ProductExtra
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed():
    async with AsyncSessionLocal() as session:
        # ── 管理員帳號 ──────────────────────────
        admin = AdminUser(
            id=uuid.uuid4(),
            email="admin@drinkshop.com",
            password_hash=pwd_context.hash("admin1234"),
            display_name="店長",
            role="owner",
            is_active=True
        )
        session.add(admin)

        # ── 商品分類 ────────────────────────────
        cat1 = Category(name="招牌飲料", sort_order=1)
        cat2 = Category(name="季節限定", sort_order=2)
        cat3 = Category(name="特調系列", sort_order=3)
        session.add_all([cat1, cat2, cat3])
        await session.flush()  # 取得 category id

        # ── 商品 ────────────────────────────────
        products = [
            Product(category_id=cat1.id, name="珍珠奶茶", description="經典台式珍珠奶茶", price_m=55, price_l=65, sort_order=1, allow_hot=True),
            Product(category_id=cat1.id, name="紅茶拿鐵", description="香醇紅茶搭配鮮奶", price_m=60, price_l=70, sort_order=2, allow_hot=True),
            Product(category_id=cat1.id, name="綠茶", description="清爽綠茶", price_m=40, price_l=50, sort_order=3, allow_hot=True),
            Product(category_id=cat1.id, name="烏龍茶", description="清香烏龍", price_m=45, price_l=55, sort_order=4, allow_hot=True),
            Product(category_id=cat2.id, name="草莓奶昔", description="季節限定草莓奶昔", price_m=75, price_l=85, sort_order=1),
            Product(category_id=cat2.id, name="芒果冰沙", description="新鮮芒果冰沙", price_m=70, price_l=80, sort_order=2),
            Product(category_id=cat3.id, name="黑糖珍珠鮮奶", description="濃郁黑糖搭配珍珠", price_m=75, price_l=85, sort_order=1, allow_hot=False),
            Product(category_id=cat3.id, name="抹茶拿鐵", description="日式抹茶鮮奶", price_m=70, price_l=80, sort_order=2, allow_hot=True),
        ]
        session.add_all(products)

        # ── 加料選項 ────────────────────────────
        extras = [
            ProductExtra(name="珍珠", price=10, sort_order=1),
            ProductExtra(name="椰果", price=10, sort_order=2),
            ProductExtra(name="布丁", price=15, sort_order=3),
            ProductExtra(name="仙草", price=10, sort_order=4),
            ProductExtra(name="芋圓", price=15, sort_order=5),
            ProductExtra(name="波霸", price=10, sort_order=6),
        ]
        session.add_all(extras)

        await session.commit()
        print("✅ Seed Data 建立完成！")
        print("─────────────────────────────")
        print("👤 管理員帳號：admin@drinkshop.com")
        print("🔑 管理員密碼：admin1234")
        print("📦 商品分類：3 個")
        print("🧋 商品：8 個")
        print("➕ 加料選項：6 個")

if __name__ == "__main__":
    asyncio.run(seed())
