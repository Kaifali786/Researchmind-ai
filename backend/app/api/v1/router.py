"""
API v1 router — aggregates all endpoint sub-routers.

This router is included once in the FastAPI application at the
``/api/v1`` prefix.
"""

from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.documents import router as documents_router
from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.notes import router as notes_router
from app.api.v1.endpoints.collections import router as collections_router
from app.api.v1.endpoints.search import router as search_router
from app.api.v1.endpoints.analytics import router as analytics_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(documents_router)
api_router.include_router(chat_router)
api_router.include_router(notes_router)
api_router.include_router(collections_router)
api_router.include_router(search_router)
api_router.include_router(analytics_router)



