from database import SessionLocal
from models import Product, CartItem, ConsultationRequest
from sqlalchemy import inspect

db = SessionLocal()

# Проверяем структуру БД
inspector = inspect(db.bind)
tables = inspector.get_table_names()

print("📋 Таблицы в базе данных:")
for table in tables:
    print(f"  - {table}")
    columns = inspector.get_columns(table)
    for col in columns:
        print(f"    * {col['name']} ({col['type']})")

# Проверяем, есть ли товары
products = db.query(Product).all()
print(f"\n📦 Товаров в базе: {len(products)}")

# Проверяем, есть ли записи в корзине
cart_items = db.query(CartItem).all()
print(f"🛒 Записей в корзине: {len(cart_items)}")

db.close()