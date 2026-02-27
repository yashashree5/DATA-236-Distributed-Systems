from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..database import get_db
from ..models import Book, Author

router = APIRouter(prefix="/books", tags=["Books"])

class BookCreate(BaseModel):
    title: str
    isbn: str
    publication_year: int
    available_copies: int = 1
    author_id: int

class BookUpdate(BaseModel):
    title: Optional[str] = None
    isbn: Optional[str] = None
    publication_year: Optional[int] = None
    available_copies: Optional[int] = None
    author_id: Optional[int] = None

class BookResponse(BaseModel):
    id: int
    title: str
    isbn: str
    publication_year: int
    available_copies: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class AuthorResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    class Config:
        from_attributes = True

class BookWithAuthor(BookResponse):
    author: AuthorResponse

class PaginatedBooks(BaseModel):
    total: int
    page: int
    page_size: int
    data: List[BookResponse]

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    author = db.query(Author).filter(Author.id == book.author_id).first()
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID {book.author_id} not found.")
    db_book = Book(**book.model_dump())
    try:
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Book with ISBN '{book.isbn}' already exists.")

@router.get("/", response_model=PaginatedBooks)
def get_all_books(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    total = db.query(Book).count()
    books = db.query(Book).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "data": books}

@router.get("/{book_id}", response_model=BookWithAuthor)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {book_id} not found.")
    return book

@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, updates: BookUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {book_id} not found.")
    if updates.author_id:
        author = db.query(Author).filter(Author.id == updates.author_id).first()
        if not author:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID {updates.author_id} not found.")
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(book, key, value)
    try:
        db.commit()
        db.refresh(book)
        return book
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="ISBN already used by another book.")

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {book_id} not found.")
    db.delete(book)
    db.commit()
