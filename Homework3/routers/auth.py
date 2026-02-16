from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Hardcoded credentials for demo purposes only
VALID_USERNAME = "admin"
VALID_PASSWORD = "password"


@router.get("/")
def home(request: Request):
    user = request.session.get("user")
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@router.get("/login")
def login_page(request: Request):
    user = request.session.get("user")
    error = request.query_params.get("error")  # ?error=1 triggers Bootstrap alert
    return templates.TemplateResponse("login.html", {"request": request, "user": user, "error": error})


@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == VALID_USERNAME and password == VALID_PASSWORD:
        request.session["user"] = username  # Store user in session
        return RedirectResponse(url="/dashboard", status_code=HTTP_302_FOUND)
    return RedirectResponse(url="/login?error=1", status_code=HTTP_302_FOUND)  # Invalid credentials


@router.get("/dashboard")
def dashboard(request: Request):
    user = request.session.get("user")
    if not user:  # Redirect to login if not authenticated
        return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})


@router.get("/logout")
def logout(request: Request):
    request.session.clear()  # Destroy session
    return RedirectResponse(url="/", status_code=HTTP_302_FOUND)