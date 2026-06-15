from fastapi import FastAPI, Request, Form, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import uuid
from typing import Optional

from database import engine, get_db
from models import Base, Product, CartItem, ConsultationRequest

# Создаем таблицы принудительно
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LOFT HAVEN")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_session_id(request: Request) -> str:
    """Получение или создание ID сессии"""
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    products = db.query(Product).limit(6).all()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "featured_products": products
    })

@app.get("/catalog", response_class=HTMLResponse)
async def catalog(
    request: Request,
    category: Optional[str] = Query(None),
    material: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    if category and category != "all":
        query = query.filter(Product.category == category)
    if material and material != "all":
        query = query.filter(Product.material == material)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    
    products = query.all()
    
    categories = db.query(Product.category).distinct().all()
    materials = db.query(Product.material).distinct().all()
    
    return templates.TemplateResponse("catalog.html", {
        "request": request,
        "products": products,
        "categories": [c[0] for c in categories],
        "materials": [m[0] for m in materials],
        "current_category": category,
        "current_material": material,
        "search_query": search
    })

@app.get("/product/{product_id}", response_class=HTMLResponse)
async def product_detail(request: Request, product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    similar = db.query(Product).filter(
        Product.category == product.category,
        Product.id != product_id
    ).limit(4).all()
    
    return templates.TemplateResponse("product.html", {
        "request": request,
        "product": product,
        "similar_products": similar
    })

@app.get("/cart", response_class=HTMLResponse)
async def cart_page(request: Request, db: Session = Depends(get_db)):
    session_id = get_session_id(request)
    
    # Получаем все товары из корзины
    cart_items = db.query(CartItem).filter(
        CartItem.session_id == session_id
    ).all()
    
    # Загружаем информацию о товарах
    cart_data = []
    total = 0
    
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            cart_data.append({
                "id": item.id,
                "product_id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": item.quantity,
                "total": product.price * item.quantity
            })
            total += product.price * item.quantity
    
    return templates.TemplateResponse("cart.html", {
        "request": request,
        "cart_items": cart_data,
        "total": total
    })

@app.post("/api/cart/add")
async def add_to_cart(
    request: Request,
    product_id: int = Form(...),
    quantity: int = Form(1),
    db: Session = Depends(get_db)
):
    session_id = get_session_id(request)
    
    # Проверяем, существует ли товар
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return JSONResponse({"success": False, "error": "Товар не найден"}, status_code=404)
    
    # Проверяем, есть ли уже такой товар в корзине
    existing = db.query(CartItem).filter(
        and_(
            CartItem.session_id == session_id,
            CartItem.product_id == product_id
        )
    ).first()
    
    if existing:
        existing.quantity += quantity
        db.commit()
        message = f"Количество товара увеличено до {existing.quantity}"
    else:
        cart_item = CartItem(
            session_id=session_id,
            product_id=product_id,
            quantity=quantity
        )
        db.add(cart_item)
        db.commit()
        message = f"Товар добавлен в корзину!"
    
    # Получаем общее количество товаров в корзине
    total_items = db.query(CartItem).filter(CartItem.session_id == session_id).count()
    
    return JSONResponse({
        "success": True,
        "cart_count": total_items,
        "message": message,
        "product_name": product.name
    })

@app.post("/api/cart/remove")
async def remove_from_cart(
    request: Request,
    item_id: int = Form(...),
    db: Session = Depends(get_db)
):
    session_id = get_session_id(request)
    
    cart_item = db.query(CartItem).filter(
        and_(
            CartItem.id == item_id,
            CartItem.session_id == session_id
        )
    ).first()
    
    if not cart_item:
        return JSONResponse({"success": False, "error": "Товар не найден в корзине"}, status_code=404)
    
    db.delete(cart_item)
    db.commit()
    
    return JSONResponse({"success": True, "message": "Товар удален из корзины"})

@app.post("/api/cart/update")
async def update_cart_quantity(
    request: Request,
    item_id: int = Form(...),
    quantity: int = Form(...),
    db: Session = Depends(get_db)
):
    session_id = get_session_id(request)
    
    cart_item = db.query(CartItem).filter(
        and_(
            CartItem.id == item_id,
            CartItem.session_id == session_id
        )
    ).first()
    
    if not cart_item:
        return JSONResponse({"success": False, "error": "Товар не найден"}, status_code=404)
    
    if quantity <= 0:
        db.delete(cart_item)
        message = "Товар удален из корзины"
    else:
        cart_item.quantity = quantity
        message = "Количество обновлено"
    
    db.commit()
    
    return JSONResponse({"success": True, "message": message})

@app.post("/api/consultation")
async def consultation(
    name: str = Form(...),
    phone: str = Form(...),
    product_name: Optional[str] = Form(None),
    comment: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    req = ConsultationRequest(
        name=name,
        phone=phone,
        product_name=product_name,
        comment=comment
    )
    db.add(req)
    db.commit()
    return JSONResponse({"success": True, "message": "Заявка отправлена! Менеджер свяжется с вами."})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)