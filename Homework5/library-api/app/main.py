from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers.authors import router as authors_router
from .routers.books import router as books_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library Management System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authors_router)
app.include_router(books_router)

@app.get("/")
def root():
    return {"message": "Library API is running!"}
