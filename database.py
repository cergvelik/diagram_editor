from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_CONFIG
from models import Base
import urllib.parse

def get_database_url(): 
    encoded_password = urllib.parse.quote_plus(DATABASE_CONFIG["password"]) # экранирование пароля
    return (f"{DATABASE_CONFIG['drivername']}://{DATABASE_CONFIG['username']}:"
            f"{encoded_password}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/"
            f"{DATABASE_CONFIG['database']}")

DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Создание таблиц в базе данных, если они отсутствуют"""
    Base.metadata.create_all(bind=engine)

def get_session():
    """Фабрика сессий для работы с БД"""
    return SessionLocal()