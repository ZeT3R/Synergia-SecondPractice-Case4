from fastapi import FastAPI, Depends, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models, database
from datetime import datetime, timedelta

app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- UI Routes ---
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin")
def admin_panel(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

# --- API Routes ---
@app.get("/api/books")
def get_books(category: str = None, author: str = None, year: int = None, db: Session = Depends(database.get_db)):
    query = db.query(models.Book)
    if category: query = query.filter(models.Book.category == category)
    if author: query = query.filter(models.Book.author == author)
    if year: query = query.filter(models.Book.year == year)
    return query.all()

@app.post("/api/books")
def add_book(title: str, author: str, year: int, category: str, price: float, db: Session = Depends(database.get_db)):
    new_book = models.Book(title=title, author=author, year=year, category=category, price=price)
    db.add(new_book)
    db.commit()
    return {"status": "success"}

@app.post("/api/rent")
def rent_book(book_id: int, duration_weeks: int, email: str, db: Session = Depends(database.get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book and book.availability:
        book.availability = False
        book.status = "Rented"
        end_date = datetime.now() + timedelta(weeks=duration_weeks)
        rental = models.Rental(book_id=book_id, user_email=email, end_date=end_date)
        db.add(rental)
        db.commit()
        return {"message": f"Rented until {end_date.date()}"}
    return {"error": "Book not available"}

@app.get("/api/admin/reminders")
def send_reminders(db: Session = Depends(database.get_db)):
    # Автоматическая проверка: если до конца аренды менее 2 дней
    now = datetime.now()
    upcoming = db.query(models.Rental).filter(models.Rental.end_date <= now + timedelta(days=2), models.Rental.reminded == False).all()
    for rent in upcoming:
        # Здесь была бы логика отправки Email
        rent.reminded = True
    db.commit()
    return {"reminders_sent": len(upcoming)}
