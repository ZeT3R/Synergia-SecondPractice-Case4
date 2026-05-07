from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Базовые поля книги
class BookBase(BaseModel):
    title: str
    author: str
    year: int
    category: str
    price: float

# Схема для создания книги (то, что присылает админ)
class BookCreate(BookBase):
    pass

# Схема для отображения книги (то, что возвращает API)
class Book(BookBase):
    id: int
    status: str
    availability: bool

    class Config:
        from_attributes = True  # Позволяет Pydantic работать с моделями SQLAlchemy

# Схема для оформления аренды
class RentalCreate(BaseModel):
    book_id: int
    duration_weeks: int
    user_email: str

# Схема для информации об аренде
class Rental(BaseModel):
    id: int
    book_id: int
    user_email: str
    end_date: datetime
    reminded: bool

    class Config:
        from_attributes = True
