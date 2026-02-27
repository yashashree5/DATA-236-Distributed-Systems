# app/models.py
# SQLAlchemy models — these map directly to your MySQL tables

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base


class Author(Base):
    __tablename__ = "authors"

    id         = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name  = Column(String(100), nullable=False)
    email      = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # One author → many books
    books = relationship("Book", back_populates="author")


class Book(Base):
    __tablename__ = "books"

    id               = Column(Integer, primary_key=True, index=True)
    title            = Column(String(255), nullable=False)
    isbn             = Column(String(20), unique=True, nullable=False, index=True)
    publication_year = Column(Integer, nullable=False)
    available_copies = Column(Integer, default=1, nullable=False)
    author_id        = Column(Integer, ForeignKey("authors.id"), nullable=False)
    created_at       = Column(DateTime, server_default=func.now())
    updated_at       = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Many books → one author
    author = relationship("Author", back_populates="books")