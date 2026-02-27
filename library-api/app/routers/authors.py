from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from ..database import get_db
from ..models import Author, Book

router = APIRouter(prefix="/authors", tags=["Authors"])

class AuthorCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

class AuthorUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None

class AuthorResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

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

class AuthorWithBooks(AuthorResponse):
    books: List[BookResponse] = []

class PaginatedAuthors(BaseModel):
    total: int
    page: int
    page_size: int
    data: List[AuthorResponse]

@router.post("/", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED)
def create_author(author: AuthorCreate, db: Session = Depends(get_db)):
    db_author = Author(**author.model_dump())
    try:
        db.add(db_author)
        db.commit()
        db.refresh(db_author)
        return db_author
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Author with email '{author.email}' already exists.")

@router.get("/", response_model=PaginatedAuthors)
def get_all_authors(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    total = db.query(Author).count()
    authors = db.query(Author).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "data": authors}

@router.get("/{author_id}", response_model=AuthorResponse)
def get_author(author_id: int, db: Session = Depends(get_db)):
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID {author_id} not found.")
    return author

@router.put("/{author_id}", response_model=AuthorResponse)
def update_author(author_id: int, updates: AuthorUpdate, db: Session = Depends(get_db)):
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID {author_id} not found.")
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(author, key, value)
    try:
        db.commit()
        db.refresh(author)
        return author
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already used by another author.")

@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(author_id: int, db: Session = Depends(get_db)):
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID {author_id} not found.")
    book_count = db.query(Book).filter(Book.author_id == author_id).count()
    if book_count > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Cannot delete author. They have {book_count} associated book(s).")
    db.delete(author)
    db.commit()

@router.get("/{author_id}/books", response_model=AuthorWithBooks)
def get_books_by_author(author_id: int, db: Session = Depends(get_db)):
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID {author_id} not found.")
    return author
