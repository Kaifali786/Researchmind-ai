from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from app.schemas.document import DocumentResponse


class CollectionCreate(BaseModel):
    """Schema for creating a collection."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="Collection display name.",
        examples=["Transformer Papers"],
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description="Optional detailed description.",
        examples=["Key architectures and analyses regarding attention mechanisms."],
    )


class CollectionUpdate(BaseModel):
    """Schema for updating an existing collection."""

    name: str | None = Field(None, min_length=1, max_length=256)
    description: str | None = Field(None, max_length=1000)


class CollectionResponse(BaseModel):
    """Read-only representation of a collection."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    description: str | None = None
    created_at: datetime
    documents: list[DocumentResponse] = Field(default_factory=list)


class CollectionListResponse(BaseModel):
    """List of all collections."""

    collections: list[CollectionResponse]
    total: int
