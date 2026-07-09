import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.note_repo import NoteRepository
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse, NoteListResponse

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post(
    "/",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new note",
)
async def create_note(
    body: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new workspace note, optionally linked to a specific paper page.
    """
    note_repo = NoteRepository(db)
    note_data = {
        "user_id": current_user.id,
        "document_id": body.document_id,
        "content": body.content,
        "note_type": body.note_type,
        "page_number": body.page_number,
        "tags": body.tags or [],
    }
    note = await note_repo.create(note_data)
    return note


@router.get(
    "/",
    response_model=NoteListResponse,
    summary="List all user notes",
)
async def list_notes(
    document_id: uuid.UUID | None = Query(None, description="Scope notes to a specific document"),
    page: int = Query(1, ge=1, description="Page offset"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve all notes written by the logged-in user, optionally filtered by paper.
    """
    note_repo = NoteRepository(db)
    skip = (page - 1) * per_page
    
    if document_id:
        notes = await note_repo.get_by_document(
            document_id=document_id,
            user_id=current_user.id,
            skip=skip,
            limit=per_page
        )
        total = len(notes)  # scoped size
    else:
        notes = await note_repo.get_by_user(
            user_id=current_user.id,
            skip=skip,
            limit=per_page
        )
        total = await note_repo.count_by_user(current_user.id)
        
    return NoteListResponse(
        notes=[NoteResponse.model_validate(n) for n in notes],
        total=total
    )


@router.get(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Get single note by ID",
)
async def get_note(
    note_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve details of a single note.
    """
    note_repo = NoteRepository(db)
    note = await note_repo.get_user_note(note_id, current_user.id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found or access denied.",
        )
    return note


@router.put(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Update an existing note",
)
async def update_note(
    note_id: uuid.UUID,
    body: NoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update note body, tags, page citation, or category.
    """
    note_repo = NoteRepository(db)
    note = await note_repo.get_user_note(note_id, current_user.id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found or access denied.",
        )

    update_data = body.model_dump(exclude_unset=True)
    updated = await note_repo.update(note_id, update_data)
    return updated


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note",
)
async def delete_note(
    note_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a note from the workspace.
    """
    note_repo = NoteRepository(db)
    deleted = await note_repo.delete_user_note(note_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found or access denied.",
        )
