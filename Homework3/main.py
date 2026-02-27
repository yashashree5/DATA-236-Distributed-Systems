import os
import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from routers.auth import router as auth_router


# ─────────────────────────────────────────────
# Concept: FastAPI App Instance
# ─────────────────────────────────────────────
# Create the main FastAPI application instance.
# This is the entry point for the whole web app.
app = FastAPI()


# ─────────────────────────────────────────────
# Concept: Secret Key for Session Security
# ─────────────────────────────────────────────
# The secret key is used to cryptographically sign the session cookie.
# os.getenv() reads from environment variables — good practice for production.
# Falls back to a hardcoded default for local development only.
# NEVER hardcode a real secret key in production.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-key")


# ─────────────────────────────────────────────
# Concept: SessionMiddleware (Starlette)
# ─────────────────────────────────────────────
# Middleware runs on every request before it reaches a route function.
# SessionMiddleware adds session support to the app:
#   - It reads/writes an encrypted cookie named "session"
#   - Routes access session data via request.session (a dict-like object)
#   - request.session.get("user") → read session
#   - request.session["user"] = value → write session
#   - request.session.clear() → destroy session (logout)
#
# Parameters:
#   secret_key  → signs the cookie so it can't be tampered with
#   https_only  → False: cookie works over HTTP (needed for localhost)
#                 True: cookie only sent over HTTPS (use in production)
#   same_site   → "lax": protects against CSRF attacks
#   max_age     → session expires after 3600 seconds (1 hour)
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    https_only=False,   # Must be False for local development (no HTTPS on localhost)
    same_site="lax",    # Prevents cross-site request forgery attacks
    max_age=3600        # Session expires after 1 hour
)


# ─────────────────────────────────────────────
# Concept: APIRouter — Modular Route Registration
# ─────────────────────────────────────────────
# Instead of defining all routes in main.py, we separate them into
# routers/auth.py using APIRouter() — this keeps code organized.
# app.include_router() plugs that mini-app into the main app.
# All routes defined in auth.py (/, /login, /dashboard, /logout)
# are now active and handled by the main app.
app.include_router(auth_router)


# ─────────────────────────────────────────────
# Concept: Running the App with Uvicorn
# ─────────────────────────────────────────────
# This block only runs when you execute: python3 main.py
# uvicorn is an ASGI server that serves the FastAPI app.
#   "main:app" → file main.py, variable app
#   reload=True → auto-restarts when code changes (development only)
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )