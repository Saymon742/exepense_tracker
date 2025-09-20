from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.database import Base, get_user_engine
from app.routes import router
from app.models import User

app = FastAPI(
    title="Expense Tracker API",
    description="API для отслеживания личных расходов",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
def startup_event():
    engine = get_user_engine(0)
    Base.metadata.create_all(bind=engine)

@app.on_event("shutdown")
def shutdown_event():
    pass

@app.get("/")
async def read_root():
    return FileResponse("app/templates/index.html")

@app.get("/dashboard")
async def get_dashboard():
    return FileResponse("app/templates/index.html")     