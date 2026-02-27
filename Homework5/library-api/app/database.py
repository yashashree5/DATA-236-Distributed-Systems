# app/database.py
# Handles the MySQL connection using SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "mysql+pymysql://root:Barclays%4011@localhost:3306/library_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# This function is used by FastAPI endpoints via Depends()
# It opens a DB session, yields it, then closes it automatically
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()