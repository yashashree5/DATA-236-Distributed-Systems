from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Optional

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


books: List[Dict] = [
    {"id": 1, "title": "Midnight’s Children", "author": "Salman Rushdie"},
    {"id": 2, "title": "The Hobbit", "author": "J.R.R. Tolkien"},
    {"id": 3, "title": "The God of Small Things", "author": "Arundhati Roy"},
    {"id": 4, "title": "1984", "author": "George Orwell"},
    {"id": 5, "title": "Malgudi Days", "author": "R. K. Narayan"},
    {"id": 6, "title": "Train to Pakistan", "author": "Khushwant Singh"},
]


def next_id() -> int:
    return max((b["id"] for b in books), default=0) + 1


def find_book(book_id: int) -> Optional[Dict]:
    return next((b for b in books if b["id"] == book_id), None)


@app.get("/")
def home(request: Request, q: str = ""):
    q = (q or "").strip()
    filtered = books
    if q:
        filtered = [b for b in books if q.lower() in b["title"].lower()]
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "books": filtered, "q": q},
    )


# ADD FORM
@app.get("/add")
def add_form(request: Request):
    return templates.TemplateResponse("add.html", {"request": request})


@app.post("/add")
def add_book(title: str = Form(...), author: str = Form(...)):
    books.append({"id": next_id(), "title": title.strip(), "author": author.strip()})
    return RedirectResponse(url="/", status_code=303)


# UPDATE FORM (generic, for row Update buttons)
@app.get("/update/{book_id}")
def update_form(request: Request, book_id: int):
    book = find_book(book_id)
    if not book:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("update.html", {"request": request, "book": book})


# UPDATE (generic)
@app.post("/update/{book_id}")
def update_book(book_id: int, title: str = Form(...), author: str = Form(...)):
    book = find_book(book_id)
    if book:
        book["title"] = title.strip()
        book["author"] = author.strip()
    return RedirectResponse(url="/", status_code=303)


# Update book ID=1 to Harry Potter / J.K Rowling
@app.post("/update-book-one")
def update_book_one():
    book = find_book(1)
    if book:
        book["title"] = "Harry Potter"
        book["author"] = "J.K Rowling"
    return RedirectResponse(url="/", status_code=303)


# DELETE CONFIRM FORM (generic)
@app.get("/delete/{book_id}")
def delete_form(request: Request, book_id: int):
    book = find_book(book_id)
    if not book:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("delete.html", {"request": request, "book": book})


# DELETE (generic) 
@app.post("/delete/{book_id}")
def delete_book(book_id: int):
    books[:] = [b for b in books if b["id"] != book_id]
    return RedirectResponse(url="/", status_code=303)


# Delete book with highest ID 
@app.post("/delete-highest-id")
def delete_highest_id():
    if books:
        highest_id = max(b["id"] for b in books)
        books[:] = [b for b in books if b["id"] != highest_id]
    return RedirectResponse(url="/", status_code=303)
