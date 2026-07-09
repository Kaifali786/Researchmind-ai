"""
ResearchMind AI FastAPI Application Entry Point.

This module initializes the FastAPI application, sets up middleware
(CORS, rate limiting), registers API routes, and configures lifespan events.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.middleware import setup_cors, setup_rate_limiting
from app.db.session import get_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for startup and shutdown verification.
    """
    # Verify database connectivity on startup
    try:
        db_generator = get_db()
        db = await anext(db_generator)
        # Execute a simple test query
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        print("Database connection verified successfully.")
    except Exception as e:
        print(f"CRITICAL: Database connection failed during startup: {e}")
    
    yield
    # Shutdown logic (if any) can go here


app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for ResearchMind AI workspace",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup Middlewares
setup_cors(app)
setup_rate_limiting(app)

# Include Router
app.include_router(api_router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root_redirect():
    """
    Redirect root access to the Swagger UI API documentation.
    """
    return RedirectResponse(url="/docs")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to intercept and format unhandled exceptions.
    """
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected internal error occurred: {str(exc)}"},
    )
