from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.sql import func
import enum

from app.database import Base

class CategoryType(str, enum.Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    SHOPPING = "shopping"
    HEALTH = "health"
    OTHER = "other"

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(Enum(CategoryType), nullable=False)
    description = Column(String, nullable=True)
    date = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())