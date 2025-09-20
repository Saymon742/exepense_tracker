from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ExpenseBase(BaseModel):
    amount: float = Field(..., gt=0)
    category: str
    description: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    date: datetime
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True

class ExpenseSummary(BaseModel):
    category: str
    total_amount: float
    count: int

class AnalyticsRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str