from sqlalchemy import func, select
from sqlalchemy.orm import Session  # Синхронный Session
from datetime import datetime
from typing import List, Optional

from app.models import Expense, CategoryType
from app.schemas import ExpenseCreate

def get_expense(db: Session, expense_id: int):
    return db.query(Expense).filter(Expense.id == expense_id).first()

def get_expenses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Expense).offset(skip).limit(limit).all()

def create_new_expense(db: Session, expense: ExpenseCreate):
    category_enum = CategoryType(expense.category)
    
    db_expense = Expense(
        amount=expense.amount,
        category=category_enum,
        description=expense.description
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def delete_expense(db: Session, expense_id: int):
    expense = get_expense(db, expense_id)
    if expense:
        db.delete(expense)
        db.commit()
        return True
    return False

def get_expenses_by_category(db: Session, category: str):
    category_enum = CategoryType(category)
    return db.query(Expense).filter(Expense.category == category_enum).all()

def get_expenses_summary(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
    query = db.query(
        Expense.category,
        func.sum(Expense.amount).label('total_amount'),
        func.count(Expense.id).label('count')
    ).group_by(Expense.category)
    
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)
    
    return query.all()

def get_total_spent(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
    query = db.query(func.sum(Expense.amount))
    
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)
    
    return query.scalar() or 0.0