from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

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

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключаем API роуты
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
async def read_root():
    # Возвращаем HTML страницу
    return FileResponse("app/templates/index.html")

@app.get("/dashboard")
async def get_dashboard():
    # Альтернативный route для dashboard
    return FileResponse("app/templates/index.html")