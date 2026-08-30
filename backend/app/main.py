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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.api.ws import router as ws_router
from app.utils.logger import setup_logging

# Set up logging first
setup_logging()

# Create the FastAPI application
app = FastAPI(
    title="EnvMan",
    description="Deterministic Environment Engine",
    version="0.1.0",
)

# CORS: Allow the frontend to talk to us
# WHY: By default, browsers block requests to different ports.
# The frontend runs on :5173, backend on :8000.
# CORS tells the browser: "It's okay, let them talk."
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect the routes
app.include_router(api_router)
app.include_router(ws_router)


@app.get("/")
async def root():
    return {"message": "EnvMan API is running"}
