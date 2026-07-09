import uuid
from typing import Any


from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.models.document import Document
from app.services.rag_service import RAGService
from pydantic import BaseModel

router = APIRouter(prefix="/search", tags=["Semantic Search"])


class SearchResultItem(BaseModel):
    """Schema for a single semantic search match."""

    content: str
    document_id: str
    document_title: str
    page_number: int
    score: float


@router.get(
    "/semantic",
    response_model=list[SearchResultItem],
    summary="Semantic vector search over library",
)
async def semantic_search(
    q: str = Query(..., min_length=1, description="The search query text"),
    limit: int = Query(10, ge=1, le=50, description="Max matches to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Search all user's uploaded papers using vector embeddings semantic search.
    """
    rag_service = RAGService(db)
    
    # Perform vector similarity search
    search_filter = {"user_id": str(current_user.id)}
    
    # LangChain's Chroma wrapper provides similarity_search_with_relevance_scores or similarity_search_with_score
    # Let's use similarity_search_with_score
    results = rag_service.vector_store.similarity_search_with_score(
        query=q,
        k=limit,
        filter=search_filter
    )

    formatted_results = []
    for doc, score in results:
        doc_id = doc.metadata.get("document_id")
        
        # Load document title from SQLite / PG
        doc_title = "Reference Document"
        try:
            doc_uuid = uuid.UUID(doc_id)
            result = await db.execute(select(Document).where(Document.id == doc_uuid))
            document = result.scalar_one_or_none()
            if document:
                doc_title = document.title
        except Exception:
            pass

        formatted_results.append(
            SearchResultItem(
                content=doc.page_content,
                document_id=doc_id,
                document_title=doc_title,
                page_number=doc.metadata.get("page_number", 1),
                score=float(score)
            )
        )
        
    return formatted_results


