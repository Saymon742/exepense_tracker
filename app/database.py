from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

Base = declarative_base()

DATABASE_DIR = "user_databases"
os.makedirs(DATABASE_DIR, exist_ok=True)

engines = {}
sessions = {}

def get_user_engine(user_id: int):
    if user_id not in engines:
        db_path = f"{DATABASE_DIR}/user_{user_id}.db"
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            echo=True
        )
        engines[user_id] = engine
    return engines[user_id]

def get_user_session(user_id: int):
    if user_id not in sessions:
        engine = get_user_engine(user_id)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        sessions[user_id] = SessionLocal
    
    return sessions[user_id]()

def create_user_tables(user_id: int):
    engine = get_user_engine(user_id)
    Base.metadata.create_all(bind=engine)