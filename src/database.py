from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQL_URL = "sqlite:///./test.db"

engine = create_engine(SQL_URL,connect_args ={"check_same_threads":False})

SessionLocal = sessionmaker(autoflush=False,autocommit = False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()