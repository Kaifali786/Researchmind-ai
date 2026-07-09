"""
Document API endpoints.

Routes:
    POST   /           — Upload a new document.
    GET    /           — List the current user's documents (paginated).
    GET    /{id}       — Retrieve a single document by ID.
    DELETE /{id}       — Delete a document by ID.
"""

import math
import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.repositories.document_repo import DocumentRepository
from app.schemas.document import DocumentCreate, DocumentListResponse, DocumentResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])
settings = get_settings()


@router.post(
    "/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new document",
    responses={
        400: {"description": "Invalid file type or file too large."},
        401: {"description": "Not authenticated."},
    },
)
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    title: str | None = None,
    abstract: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DocumentResponse:
    """
    Upload a research document (PDF, DOCX, TXT, etc.).

    The file is persisted to disk in a user-specific directory, a
    database record is created, and a background task is queued for
    processing and chunking.

    Args:
        file: The uploaded file.
        background_tasks: FastAPI BackgroundTasks queue.
        title: Optional human-readable title (defaults to filename).
        abstract: Optional abstract.
        db: Async database session.
        current_user: Authenticated user.

    Returns:
        The created document record.

    Raises:
        HTTPException 400: Unsupported file extension or file too large.
    """
    # ── Validate extension ───────────────────────────────────────────
    filename = file.filename or "untitled"
    extension = Path(filename).suffix.lower()

    if extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{extension}' is not supported. "
                   f"Allowed: {', '.join(sorted(settings.ALLOWED_EXTENSIONS))}",
        )

    # ── Read and validate size ───────────────────────────────────────
    contents = await file.read()
    file_size = len(contents)

    if file_size > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size ({file_size} bytes) exceeds the "
                   f"{settings.MAX_UPLOAD_SIZE_MB} MB limit.",
        )

    # ── Persist to disk ──────────────────────────────────────────────
    user_upload_dir = Path(settings.UPLOAD_DIR) / str(current_user.id)
    user_upload_dir.mkdir(parents=True, exist_ok=True)

    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    file_path = user_upload_dir / unique_filename

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(contents)

    # ── Create DB record ─────────────────────────────────────────────
    doc_repo = DocumentRepository(db)
    doc = await doc_repo.create(
        {
            "user_id": current_user.id,
            "title": title or filename,
            "filename": filename,
            "file_type": file.content_type or extension,
            "file_path": str(file_path),
            "file_size": file_size,
            "abstract": abstract,
        }
    )

    # ── Enqueue Background Processing ────────────────────────────────
    doc_service = DocumentService(db)
    background_tasks.add_task(doc_service.process_document, doc.id)

    return DocumentResponse.model_validate(doc)



@router.get(
    "/",
    response_model=DocumentListResponse,
    summary="List documents",
    responses={
        401: {"description": "Not authenticated."},
    },
)
async def list_documents(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DocumentListResponse:
    """
    Retrieve a paginated list of the current user's documents.

    Args:
        page: Page number (1-indexed).
        per_page: Number of documents per page.
        db: Async database session.
        current_user: Authenticated user.

    Returns:
        Paginated document list with total count and page metadata.
    """
    doc_repo = DocumentRepository(db)
    skip = (page - 1) * per_page

    documents = await doc_repo.get_by_user(
        current_user.id, skip=skip, limit=per_page
    )
    total = await doc_repo.count_by_user(current_user.id)
    total_pages = math.ceil(total / per_page) if total > 0 else 0

    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(d) for d in documents],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get a document by ID",
    responses={
        401: {"description": "Not authenticated."},
        404: {"description": "Document not found."},
    },
)
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DocumentResponse:
    """
    Retrieve a single document by its UUID.

    Only the owning user can access the document.

    Args:
        document_id: UUID of the target document.
        db: Async database session.
        current_user: Authenticated user.

    Returns:
        The document detail.

    Raises:
        HTTPException 404: Document not found or not owned by the user.
    """
    doc_repo = DocumentRepository(db)
    doc = await doc_repo.get_user_document(document_id, current_user.id)

    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return DocumentResponse.model_validate(doc)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document",
    responses={
        401: {"description": "Not authenticated."},
        404: {"description": "Document not found."},
    },
)
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a document and its associated file on disk.

    Only the owning user can delete the document. The physical file is
    removed from storage after the DB record is deleted.

    Args:
        document_id: UUID of the target document.
        db: Async database session.
        current_user: Authenticated user.

    Raises:
        HTTPException 404: Document not found or not owned by the user.
    """
    doc_repo = DocumentRepository(db)

    # Fetch first to get file_path for cleanup
    doc = await doc_repo.get_user_document(document_id, current_user.id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    file_path = doc.file_path

    deleted = await doc_repo.delete_user_document(document_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    # ── Cleanup physical file ────────────────────────────────────────
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            # Log but don't fail the request – the DB record is already gone
            pass


# ── AI Reading Features (Phase 4) ──────────────────────────────────
from typing import Any
from pydantic import BaseModel, Field
from app.services.reading_service import ReadingService


class ExplainRequest(BaseModel):
    text: str = Field(..., description="Paragraph text to simplify.")


class SummaryResponse(BaseModel):
    summary: str


class KeyIdeasResponse(BaseModel):
    key_ideas: list[str]


class BulletNotesResponse(BaseModel):
    notes: str


class ExplainResponse(BaseModel):
    explanation: str


@router.post(
    "/{document_id}/summarize",
    response_model=SummaryResponse,
    summary="Get document executive summary",
)
async def summarize_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Generate a high-fidelity Markdown summary of the paper."""
    doc_repo = DocumentRepository(db)
    doc = await doc_repo.get_user_document(document_id, current_user.id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )
    
    reading_service = ReadingService(db)
    summary_text = await reading_service.summarize_document(document_id)
    return SummaryResponse(summary=summary_text)


@router.post(
    "/{document_id}/key-ideas",
    response_model=KeyIdeasResponse,
    summary="Extract document key ideas",
)
async def extract_key_ideas(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Extract top scientific takeaways and contributions from the paper."""
    doc_repo = DocumentRepository(db)
    doc = await doc_repo.get_user_document(document_id, current_user.id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )
        
    reading_service = ReadingService(db)
    ideas = await reading_service.extract_key_ideas(document_id)
    return KeyIdeasResponse(key_ideas=ideas)


@router.post(
    "/{document_id}/bullet-notes",
    response_model=BulletNotesResponse,
    summary="Generate bullet-point reading notes",
)
async def generate_bullet_notes(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Produce organized bulleted notes from the paper sections."""
    doc_repo = DocumentRepository(db)
    doc = await doc_repo.get_user_document(document_id, current_user.id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )
        
    reading_service = ReadingService(db)
    notes_text = await reading_service.generate_bullet_notes(document_id)
    return BulletNotesResponse(notes=notes_text)


@router.post(
    "/explain",
    response_model=ExplainResponse,
    summary="Explain and simplify technical jargon",
)
async def explain_text(
    body: ExplainRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Translate highly technical paragraphs or math concepts into simpler terms."""
    reading_service = ReadingService(db)
    explanation = await reading_service.explain_text(body.text)
    return ExplainResponse(explanation=explanation)


# ── Research Tools (Phase 5) ──────────────────────────────────────
from app.services.research_service import ResearchService


class CompareRequest(BaseModel):
    document_ids: list[uuid.UUID]


class LitReviewRequest(BaseModel):
    document_ids: list[uuid.UUID]


class CitationsResponse(BaseModel):
    apa: str
    mla: str
    ieee: str
    chicago: str
    bibtex: str


class GapFinderResponse(BaseModel):
    analysis: str


class LitReviewResponse(BaseModel):
    review: str


@router.post(
    "/compare",
    response_model=list[dict],
    summary="Compare multiple papers",
)
async def compare_papers(
    body: CompareRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Extract and compile a side-by-side comparison matrix for multiple research papers."""
    # Verify access to all requested documents
    doc_repo = DocumentRepository(db)
    for doc_id in body.document_ids:
        doc = await doc_repo.get_user_document(doc_id, current_user.id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {doc_id} not found or access denied.",
            )

    research_service = ResearchService(db)
    return await research_service.compare_papers(body.document_ids)


@router.post(
    "/{document_id}/gap-finder",
    response_model=GapFinderResponse,
    summary="Find research gaps",
)
async def identify_research_gaps(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Find open problems, methodologies shortcomings, or future work opportunities in a paper."""
    doc_repo = DocumentRepository(db)
    doc = await doc_repo.get_user_document(document_id, current_user.id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    research_service = ResearchService(db)
    res = await research_service.identify_research_gaps(document_id)
    return GapFinderResponse(analysis=res["analysis"])


@router.post(
    "/{document_id}/citations",
    response_model=CitationsResponse,
    summary="Generate citations",
)
async def generate_citations(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Generate professional citations for the paper in APA, MLA, IEEE, Chicago, and BibTeX."""
    doc_repo = DocumentRepository(db)
    doc = await doc_repo.get_user_document(document_id, current_user.id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    research_service = ResearchService(db)
    res = await research_service.generate_citations(document_id)
    return CitationsResponse(**res)


@router.post(
    "/literature-review",
    response_model=LitReviewResponse,
    summary="Generate literature review synthesis",
)
async def generate_literature_review(
    body: LitReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Write a cohesive Literature Review synthesizing the selected research papers."""
    doc_repo = DocumentRepository(db)
    for doc_id in body.document_ids:
        doc = await doc_repo.get_user_document(doc_id, current_user.id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {doc_id} not found or access denied.",
            )

    research_service = ResearchService(db)
    review_text = await research_service.generate_literature_review(body.document_ids)
    return LitReviewResponse(review=review_text)


class GraphNode(BaseModel):
    id: str
    label: str
    type: str


class GraphLink(BaseModel):
    source: str
    target: str
    type: str


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    links: list[GraphLink]


@router.get(
    "/{document_id}/graph",
    response_model=GraphResponse,
    summary="Get document knowledge graph",
)
async def get_document_graph(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Generate author-topic-keyword graph visualization nodes/links for the paper."""
    doc_repo = DocumentRepository(db)
    doc = await doc_repo.get_user_document(document_id, current_user.id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )
    
    research_service = ResearchService(db)
    graph_data = await research_service.extract_knowledge_graph(document_id)
    return GraphResponse(
        nodes=graph_data.get("nodes", []),
        links=graph_data.get("links", [])
    )



