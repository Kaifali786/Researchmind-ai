"""
Pydantic v2 schemas for document endpoints.

Covers upload metadata, single-document detail, and paginated list responses.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    """
    Metadata submitted alongside a file upload.

    The actual file bytes are sent as ``UploadFile``; this schema
    captures the optional metadata fields.
    """

    title: str | None = Field(
        None,
        max_length=512,
        description="Document title. Defaults to the original filename.",
        examples=["Attention Is All You Need"],
    )
    abstract: str | None = Field(
        None,
        description="Optional abstract or summary.",
    )
    metadata: dict | None = Field(
        None,
        description="Arbitrary JSON metadata (authors, DOI, tags, etc.).",
        examples=[{"authors": ["Vaswani et al."], "year": 2017}],
    )


class DocumentChunkResponse(BaseModel):
    """Read-only representation of a single document chunk."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    chunk_index: int
    content: str
    page_number: int | None = None
    section: str | None = None
    embedding_id: str | None = None


class DocumentResponse(BaseModel):
    """Full detail of a single document."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    filename: str
    file_type: str
    file_size: int
    abstract: str | None = None
    metadata: dict | None = Field(None, alias="metadata_")
    status: str
    page_count: int | None = None
    uploaded_at: datetime
    processed_at: datetime | None = None


class DocumentListResponse(BaseModel):
    """Paginated list of documents."""

    documents: list[DocumentResponse]
    total: int = Field(..., description="Total number of documents matching the query.")
    page: int = Field(..., ge=1, description="Current page number.")
    per_page: int = Field(..., ge=1, le=100, description="Items per page.")
    total_pages: int = Field(..., ge=0, description="Total number of pages.")
