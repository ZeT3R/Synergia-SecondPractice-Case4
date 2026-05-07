from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from database import Base
import datetime

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    year = Column(Integer)
    category = Column(String)
    price = Column(Float)
    status = Column(String, default="Available") # Available, Rented, Sold
    availability = Column(Boolean, default=True)

class Rental(Base):
    __tablename__ = "rentals"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer)
    user_email = Column(String)
    end_date = Column(DateTime)
    reminded = Column(Boolean, default=False)
