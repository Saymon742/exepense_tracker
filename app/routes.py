from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session  # Синхронный Session
from typing import List, Optional
from datetime import datetime

from app.crud import (
    get_expense, get_expenses, create_new_expense, delete_expense,
    get_expenses_by_category, get_expenses_summary, get_total_spent
)
from app.schemas import Expense, ExpenseCreate, ExpenseSummary
from app.utils import generate_expense_chart, generate_csv_report
from app.database import get_db

router = APIRouter()

@router.post("/expenses/", response_model=Expense)
def create_expense_route(expense: ExpenseCreate, db: Session = Depends(get_db)):
    return create_new_expense(db=db, expense=expense)

@router.get("/expenses/", response_model=List[Expense])
def read_expenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    expenses = get_expenses(db, skip=skip, limit=limit)
    return expenses

@router.get("/expenses/{expense_id}", response_model=Expense)
def read_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = get_expense(db, expense_id=expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@router.delete("/expenses/{expense_id}")
def delete_expense_route(expense_id: int, db: Session = Depends(get_db)):
    success = delete_expense(db, expense_id=expense_id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}

@router.get("/expenses/category/{category}", response_model=List[Expense])
def read_expenses_by_category(category: str, db: Session = Depends(get_db)):
    return get_expenses_by_category(db, category=category)

@router.get("/analytics/summary", response_model=List[ExpenseSummary])
def get_summary(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    summary = get_expenses_summary(db, start_date, end_date)
    return [
        ExpenseSummary(
            category=item[0].value,
            total_amount=float(item[1]),
            count=int(item[2])
        )
        for item in summary
    ]

@router.get("/analytics/total")
def get_total(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    total = get_total_spent(db, start_date, end_date)
    return {"total_amount": float(total)}

@router.get("/analytics/chart")
def get_chart(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    summary = get_expenses_summary(db, start_date, end_date)
    chart_data = generate_expense_chart(summary)
    return {"chart": chart_data}

@router.get("/analytics/report")
def get_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    summary = get_expenses_summary(db, start_date, end_date)
    csv_data = generate_csv_report(summary)
    return {
        "csv": csv_data,
        "filename": f"expense_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    }