from sqlalchemy.orm import Session
from app.models import Expense, User, CategoryType
from app.schemas import ExpenseCreate, UserCreate
from app.utils import get_password_hash
from typing import List, Optional
from datetime import datetime

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password, hashed_password):
    from app.utils import verify_password as verify_pass
    return verify_pass(plain_password, hashed_password)

def get_expense(db: Session, expense_id: int, user_id: int):
    return db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user_id).first()

def get_expenses(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Expense).filter(Expense.user_id == user_id).offset(skip).limit(limit).all()

def create_new_expense(db: Session, expense: ExpenseCreate, user_id: int):
    try:
        # Преобразуем строку в CategoryType
        category_enum = CategoryType(expense.category)
        db_expense = Expense(
            amount=expense.amount,
            category=category_enum,
            description=expense.description,
            user_id=user_id
        )
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
        return db_expense
    except ValueError as e:
        # Если категория невалидна
        raise ValueError(f"Invalid category: {expense.category}")

def delete_expense(db: Session, expense_id: int, user_id: int):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user_id).first()
    if expense:
        db.delete(expense)
        db.commit()
        return True
    return False

def get_expenses_by_category(db: Session, category: str, user_id: int):
    try:
        category_enum = CategoryType(category)
        return db.query(Expense).filter(
            Expense.category == category_enum, 
            Expense.user_id == user_id
        ).all()
    except ValueError:
        return []

def get_expenses_summary(db: Session, start_date: Optional[datetime], end_date: Optional[datetime], user_id: int):
    query = db.query(
        Expense.category,
        db.func.sum(Expense.amount),
        db.func.count(Expense.id)
    ).filter(Expense.user_id == user_id)
    
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)
    
    return query.group_by(Expense.category).all()

def get_total_spent(db: Session, start_date: Optional[datetime], end_date: Optional[datetime], user_id: int):
    query = db.query(db.func.sum(Expense.amount)).filter(Expense.user_id == user_id)
    
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)
    
    return query.scalar() or 0.0