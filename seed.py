from database import SessionLocal
from models import Product, Base
from database import engine

print("Заполнение базы данных...")

Base.metadata.create_all(bind=engine)
db = SessionLocal()

existing = db.query(Product).first()
if existing:
    print("Товары уже есть в базе")
    db.close()
    exit()

products = [
    Product(
        name="Лофт-стол Индустриал",
        category="Кабинет",
        material="Металл",
        price=54900,
        description="Письменный стол в индустриальном стиле",
        specifications="Сталь, массив дуба. 160x80 см"
    ),
    Product(
        name="Кресло Чикаго",
        category="Гостиная",
        material="Дерево",
        price=39900,
        description="Кресло из массива бука",
        specifications="Экокожа, 85x90 см"
    ),
    Product(
        name="Стеллаж Бруклин",
        category="Гостиная",
        material="Металл",
        price=47800,
        description="Стеллаж с полками из стекла",
        specifications="Сталь, стекло. 180x120 см"
    ),
    Product(
        name="Кровать Лофт Мастер",
        category="Спальня",
        material="Дерево",
        price=129900,
        description="Двуспальная кровать",
        specifications="Массив ясеня, 160x200 см"
    ),
    Product(
        name="Обеденный стол Tribeca",
        category="Столовая",
        material="Сочетание",
        price=87900,
        description="Стол со стальным основанием",
        specifications="Дуб, сталь. 200x90 см"
    ),
]

for product in products:
    db.add(product)

db.commit()
print(f"Добавлено {len(products)} товаров")
db.close()