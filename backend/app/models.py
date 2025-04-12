import os
from .config import DefaultConfig

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy.orm import sessionmaker, relationship  # type: ignore
from sqlalchemy.sql import expression
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date
from datetime import datetime



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def db_reset():
    """Veritabanını sıfırlamak için hazırlan fonksiyon"""
    Base.metadata.reflect(bind=engine)
    Base.metadata.drop_all(bind=engine)
