import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.models.collection import Collection
from app.models.document import Document
from app.schemas.collection import (
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse,
    CollectionListResponse,
)

router = APIRouter(prefix="/collections", tags=["Collections"])


@router.post(
    "/",
    response_model=CollectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new collection",
)
async def create_collection(
    body: CollectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new named group/folder for organizing research papers.
    """
    collection = Collection(
        user_id=current_user.id,
        name=body.name,
        description=body.description,
    )
    db.add(collection)
    await db.commit()
    await db.refresh(collection)
    return collection


@router.get(
    "/",
    response_model=CollectionListResponse,
    summary="List all user collections",
)
async def list_collections(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve all collections created by the logged-in user.
    """
    result = await db.execute(
        select(Collection)
        .where(Collection.user_id == current_user.id)
        .order_by(Collection.created_at.desc())
    )
    collections = result.scalars().all()
    return CollectionListResponse(
        collections=[CollectionResponse.model_validate(c) for c in collections],
        total=len(collections),
    )


@router.get(
    "/{collection_id}",
    response_model=CollectionResponse,
    summary="Get collection by ID",
)
async def get_collection(
    collection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve a single collection along with all its grouped documents.
    """
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == current_user.id,
        )
    )
    collection = result.scalars().first()
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found.",
        )
    return collection


@router.put(
    "/{collection_id}",
    response_model=CollectionResponse,
    summary="Update collection",
)
async def update_collection(
    collection_id: uuid.UUID,
    body: CollectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a collection name or description.
    """
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == current_user.id,
        )
    )
    collection = result.scalars().first()
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found.",
        )

    if body.name is not None:
        collection.name = body.name
    if body.description is not None:
        collection.description = body.description

    await db.commit()
    await db.refresh(collection)
    return collection


@router.delete(
    "/{collection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete collection",
)
async def delete_collection(
    collection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a collection folder (does not delete physical documents).
    """
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == current_user.id,
        )
    )
    collection = result.scalars().first()
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found.",
        )

    await db.delete(collection)
    await db.commit()


from pydantic import BaseModel


class LinkDocumentRequest(BaseModel):
    document_id: uuid.UUID



@router.post(
    "/{collection_id}/documents",
    response_model=CollectionResponse,
    summary="Add a document to a collection",
)
async def add_document_to_collection(
    collection_id: uuid.UUID,
    body: LinkDocumentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Add a research document into a collection.
    """
    # 1. Fetch collection
    result_col = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == current_user.id,
        )
    )
    collection = result_col.scalars().first()
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found.",
        )

    # 2. Fetch document (verifying ownership)
    result_doc = await db.execute(
        select(Document).where(
            Document.id == body.document_id,
            Document.user_id == current_user.id,
        )
    )
    document = result_doc.scalars().first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied.",
        )

    if document not in collection.documents:
        collection.documents.append(document)
        await db.commit()
        await db.refresh(collection)

    return collection


@router.delete(
    "/{collection_id}/documents/{document_id}",
    response_model=CollectionResponse,
    summary="Remove a document from a collection",
)
async def remove_document_from_collection(
    collection_id: uuid.UUID,
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Remove a document association from a collection.
    """
    result_col = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == current_user.id,
        )
    )
    collection = result_col.scalars().first()
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found.",
        )

    result_doc = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    document = result_doc.scalars().first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    if document in collection.documents:
        collection.documents.remove(document)
        await db.commit()
        await db.refresh(collection)

    return collection
