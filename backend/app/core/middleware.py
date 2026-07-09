"""
Middleware configuration — CORS and rate limiting.

Provides factory functions that attach middleware to the FastAPI app
instance during startup.
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import get_settings


def _get_key_func(request: Request) -> str:
    """
    Key function for slowapi rate limiter.

    Uses the client's remote IP address as the rate-limit key.

    Args:
        request: The incoming HTTP request.

    Returns:
        A string key identifying the client.
    """
    return get_remote_address(request)


# ── Limiter singleton ────────────────────────────────────────────────────────

limiter = Limiter(key_func=_get_key_func)


def setup_cors(app: FastAPI) -> None:
    """
    Attach CORS middleware to the application.

    Reads allowed origins from application settings.

    Args:
        app: The FastAPI application instance.
    """
    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Page", "X-Per-Page"],
    )


def setup_rate_limiting(app: FastAPI) -> None:
    """
    Attach the slowapi rate limiter to the application.

    Registers the limiter in ``app.state`` and installs the
    ``429 Too Many Requests`` error handler.

    Args:
        app: The FastAPI application instance.
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
