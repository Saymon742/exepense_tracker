from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Синхронные импорты
from app.database import engine, Base
from app.routes import router

app = FastAPI(
    title="Expense Tracker API",
    description="API для отслеживания личных расходов",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
def startup_event():
    # Синхронное создание таблиц
    Base.metadata.create_all(bind=engine)

@app.on_event("shutdown")
def shutdown_event():
    # Очищаем ресурсы при завершении
    engine.dispose()

@app.get("/")
def read_root():
    return {
        "message": "Добро пожаловать в Expense Tracker API!",
        "docs": "/docs",
        "version": "1.0.0"
    }