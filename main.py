from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional

import models, database, schemas

app = FastAPI()

# Инициализация БД
models.Base.metadata.create_all(bind=database.engine)

# Подключение статики и шаблонов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- UI ROUTES (Рендеринг страниц) ---

@app.get("/")
def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin")
def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

# --- API ROUTES (Работа с данными) ---

# Получение списка книг с фильтрацией
@app.get("/api/books", response_model=List[schemas.Book])
def get_books(
    category: Optional[str] = None, 
    author: Optional[str] = None, 
    year: Optional[int] = None, 
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Book)
    if category:
        query = query.filter(models.Book.category.ilike(f"%{category}%"))
    if author:
        query = query.filter(models.Book.author.ilike(f"%{author}%"))
    if year:
        query = query.filter(models.Book.year == year)
    return query.all()

# Добавление новой книги (Админ)
@app.post("/api/books", status_code=201)
def create_book(book: schemas.BookCreate, db: Session = Depends(database.get_db)):
    db_book = models.Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return {"status": "Book added successfully"}

# Аренда книги
@app.post("/api/rent")
def rent_book(rental_info: schemas.RentalCreate, db: Session = Depends(database.get_db)):
    book = db.query(models.Book).filter(models.Book.id == rental_info.book_id).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book.availability:
        raise HTTPException(status_code=400, detail="Book is already rented or sold")

    # Обновляем статус книги
    book.availability = False
    book.status = "Rented"
    
    # Рассчитываем дату возврата
    end_date = datetime.now() + timedelta(weeks=rental_info.duration_weeks)
    
    rental_entry = models.Rental(
        book_id=book.id,
        user_email=rental_info.user_email,
        end_date=end_date
    )
    
    db.add(rental_entry)
    db.commit()
    return {"message": f"Successfully rented until {end_date.strftime('%Y-%m-%d')}"}

# Автоматическое напоминание (Админ)
@app.get("/api/admin/reminders")
def process_reminders(db: Session = Depends(database.get_db)):
    # Ищем аренды, срок которых истекает через 2 дня или меньше
    deadline = datetime.now() + timedelta(days=2)
    expiring_rentals = db.query(models.Rental).filter(
        models.Rental.end_date <= deadline,
        models.Rental.reminded == False
    ).all()
    
    count = 0
    for rental in expiring_rentals:
        # Логика отправки письма была бы здесь
        rental.reminded = True
        count += 1
    
    db.commit()
    return {"reminders_sent": count}

# Изменение цены или статуса (Админ)
@app.patch("/api/books/{book_id}")
def update_book_status(book_id: int, price: float = None, available: bool = None, db: Session = Depends(database.get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if price is not None: book.price = price
    if available is not None: 
        book.availability = available
        book.status = "Available" if available else "Unavailable"
        
    db.commit()
    return {"status": "updated"}
