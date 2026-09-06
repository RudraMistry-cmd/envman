"""
Main Application
================

WHY: FastAPI needs a main entry point.
     This file creates the app and connects all the pieces.

WHAT:
     1. Creates the FastAPI app
     2. Adds CORS middleware (so the frontend can talk to us)
     3. Includes the HTTP routes (POST /setup, GET /health)
     4. Includes the WebSocket handler (WS /ws)
     5. Sets up logging

THINK OF IT LIKE:
     The front desk of a hotel.
     - Guests (frontend) arrive
     - Front desk routes them to the right place
     - Housekeeping (engine) does the work
     - Front desk sends updates back to the guest
"""

import mimetypes
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import router as api_router
from app.api.ws import router as ws_router
from app.utils.logger import setup_logging

# Ensure correct MIME types on Windows where registry may map .js to text/plain
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/svg+xml", ".svg")

# Set up logging first
setup_logging()

# Create the FastAPI application
app = FastAPI(
    title="EnvMan",
    description="Deterministic Environment Engine",
    version="0.1.0",
)

# CORS: Allow both packaged same-origin requests and local dev servers (:5173 / :8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "tauri://localhost",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect the API and WebSocket routes first so they take precedence
app.include_router(api_router)
app.include_router(ws_router)

# Mount bundled static files at "/" if available; otherwise provide fallback root
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.is_dir() and (STATIC_DIR / "index.html").is_file():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
else:
    @app.get("/")
    async def root():
        return {"message": "EnvMan API is running"}

