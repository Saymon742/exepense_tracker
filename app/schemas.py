from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ExpenseBase(BaseModel):
    amount: float = Field(..., gt=0, description="Сумма расхода должна быть положительной")
    category: str
    description: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    date: datetime
    created_at: datetime

    class Config:
        orm_mode = True  # Для Pydantic v1

class ExpenseSummary(BaseModel):
    category: str
    total_amount: float
    count: int

class AnalyticsRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None