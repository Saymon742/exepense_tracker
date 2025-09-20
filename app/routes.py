from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.crud import (
    get_expense, get_expenses, create_new_expense, delete_expense,
    get_expenses_by_category, get_expenses_summary, get_total_spent,
    create_user, get_user_by_username, verify_password
)
from app.schemas import Expense, ExpenseCreate, ExpenseSummary, UserCreate, User, Token
from app.utils import create_access_token, generate_expense_chart, generate_csv_report
from app.database import get_user_session, create_user_tables
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

def get_current_user_id(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        return int(form_data.username)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID")

@router.post("/register", response_model=User)
def register_user(user: UserCreate):
    db = get_user_session(0)
    try:
        db_user = get_user_by_username(db, user.username)
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        new_user = create_user(db, user)
        create_user_tables(new_user.id)
        return new_user
    finally:
        db.close()

@router.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_user_session(0)
    try:
        user = get_user_by_username(db, form_data.username)
        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        db.close()

@router.post("/expenses/", response_model=Expense)
def create_expense_route(
    expense: ExpenseCreate, 
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_id: int = Depends(get_current_user_id)
):
    db = get_user_session(user_id)
    try:
        return create_new_expense(db=db, expense=expense, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating expense: {str(e)}")
    finally:
        db.close()

@router.get("/expenses/", response_model=List[Expense])
def read_expenses(
    skip: int = 0, 
    limit: int = 100, 
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_id: int = Depends(get_current_user_id)
):
    db = get_user_session(user_id)
    try:
        expenses = get_expenses(db, user_id=user_id, skip=skip, limit=limit)
        return expenses
    finally:
        db.close()

@router.get("/expenses/{expense_id}", response_model=Expense)
def read_expense(
    expense_id: int, 
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_id: int = Depends(get_current_user_id)
):
    db = get_user_session(user_id)
    try:
        expense = get_expense(db, expense_id=expense_id, user_id=user_id)
        if expense is None:
            raise HTTPException(status_code=404, detail="Expense not found")
        return expense
    finally:
        db.close()

@router.delete("/expenses/{expense_id}")
def delete_expense_route(
    expense_id: int, 
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_id: int = Depends(get_current_user_id)
):
    db = get_user_session(user_id)
    try:
        success = delete_expense(db, expense_id=expense_id, user_id=user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Expense not found")
        return {"message": "Expense deleted successfully"}
    finally:
        db.close()

@router.get("/expenses/category/{category}", response_model=List[Expense])
def read_expenses_by_category(
    category: str, 
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_id: int = Depends(get_current_user_id)
):
    db = get_user_session(user_id)
    try:
        return get_expenses_by_category(db, category=category, user_id=user_id)
    finally:
        db.close()

@router.get("/analytics/summary", response_model=List[ExpenseSummary])
def get_summary(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_id: int = Depends(get_current_user_id)
):
    db = get_user_session(user_id)
    try:
        summary = get_expenses_summary(db, start_date, end_date, user_id)
        return [
            ExpenseSummary(
                category=str(item[0]),
                total_amount=float(item[1]),
                count=int(item[2])
            )
            for item in summary
        ]
    finally:
        db.close()

@router.get("/analytics/total")
def get_total(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_id: int = Depends(get_current_user_id)
):
    db = get_user_session(user_id)
    try:
        total = get_total_spent(db, start_date, end_date, user_id)
        return {"total_amount": float(total)}
    finally:
        db.close()

@router.get("/analytics/chart")
def get_chart(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_id: int = Depends(get_current_user_id)
):
    db = get_user_session(user_id)
    try:
        summary = get_expenses_summary(db, start_date, end_date, user_id)
        chart_data = generate_expense_chart(summary)
        return {"chart": chart_data}
    finally:
        db.close()

@router.get("/analytics/report")
def get_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_id: int = Depends(get_current_user_id)
):
    db = get_user_session(user_id)
    try:
        summary = get_expenses_summary(db, start_date, end_date, user_id)
        csv_data = generate_csv_report(summary)
        return {
            "csv": csv_data,
            "filename": f"expense_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    finally:
        db.close()

# Тестовый маршрут без аутентификации
@router.post("/test-expense/", response_model=Expense)
def test_create_expense(expense: ExpenseCreate):
    db = get_user_session(1)
    try:
        return create_new_expense(db=db, expense=expense, user_id=1)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating expense: {str(e)}")
    finally:
        db.close()