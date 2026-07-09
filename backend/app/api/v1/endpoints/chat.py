import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage, MessageRole
from app.repositories.base import BaseRepository
from app.schemas.chat import (
    ChatCreate,
    ChatResponse,
    ChatListResponse,
    MessageCreate,
    MessageResponse,
)
from app.services.rag_service import RAGService
from pydantic import BaseModel, Field

router = APIRouter(prefix="/chat", tags=["Chat"])


class AskRequest(BaseModel):
    """Schema for a direct question over a document."""

    document_id: uuid.UUID | None = Field(
        default=None,
        description="Optional document ID to scope the RAG retrieval.",
    )
    question: str = Field(
        ...,
        min_length=1,
        description="The query / question text.",
    )


class AskResponse(BaseModel):
    """Schema for direct question response."""

    content: str
    confidence_score: float
    citations: list[dict] = Field(default_factory=list)


@router.post(
    "/",
    response_model=AskResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question about a document (RAG)",
)
async def ask_question(
    body: AskRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Submit a question over a specific document or all documents in the user's library.
    
    Generates a response backed by semantic chunks retrieved from ChromaDB.
    """
    rag_service = RAGService(db)
    result = await rag_service.answer_question(
        user_id=current_user.id,
        question=body.question,
        document_id=body.document_id,
    )
    return AskResponse(
        content=result["answer"],
        confidence_score=result["confidence_score"],
        citations=result["citations"],
    )


@router.post(
    "/sessions",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat session",
)
async def create_session(
    body: ChatCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Start a new chat thread for user Q&A.
    """
    session = ChatSession(
        user_id=current_user.id,
        title=body.title,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get(
    "/sessions",
    response_model=ChatListResponse,
    summary="List all chat sessions",
)
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve all conversation threads created by the logged-in user.
    """
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.created_at.desc())
    )
    sessions = result.scalars().all()
    return ChatListResponse(
        sessions=[ChatResponse.model_validate(s) for s in sessions],
        total=len(sessions),
    )


@router.get(
    "/sessions/{session_id}",
    response_model=ChatResponse,
    summary="Get a chat session details",
)
async def get_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve message history for a specific chat session.
    """
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found.",
        )
    return session


@router.post(
    "/sessions/{session_id}/messages",
    response_model=MessageResponse,
    summary="Post a message in a session",
)
async def post_message(
    session_id: uuid.UUID,
    body: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Post a user message in a chat session and generate an assistant response.
    """
    # 1. Verify session ownership
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found.",
        )

    # 2. Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        role=MessageRole.USER,
        content=body.content,
    )
    db.add(user_msg)
    await db.commit()

    # 3. Trigger RAG answer generation (using RAGService)
    rag_service = RAGService(db)
    # Default to scope within the entire user library for general questions in session
    rag_res = await rag_service.answer_question(
        user_id=current_user.id,
        question=body.content,
    )

    # 4. Save AI Response
    assistant_msg = ChatMessage(
        session_id=session.id,
        role=MessageRole.ASSISTANT,
        content=rag_res["answer"],
        confidence_score=rag_res["confidence_score"],
        citations=rag_res["citations"],
    )
    db.add(assistant_msg)
    await db.commit()
    await db.refresh(assistant_msg)

    return assistant_msg
