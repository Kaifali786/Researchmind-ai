from typing import Any
import uuid

from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
import io

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.models.document import Document
from app.models.note import Note
from pydantic import BaseModel

router = APIRouter(prefix="/analytics", tags=["Analytics"])


class AnalyticsOverview(BaseModel):
    total_papers: int
    total_notes: int
    file_type_distribution: dict[str, int]
    top_tags: list[dict[str, Any]]
    recent_activity: list[dict[str, Any]]


class TimelineItem(BaseModel):
    id: uuid.UUID
    title: str
    year: int
    filename: str


@router.get(
    "/overview",
    response_model=AnalyticsOverview,
    summary="Get user research analytics overview",
)
async def get_analytics_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get aggregated statistics regarding the user's research workspace activity.
    """
    # 1. Total papers count
    papers_result = await db.execute(
        select(func.count(Document.id)).where(Document.user_id == current_user.id)
    )
    total_papers = papers_result.scalar_one()

    # 2. Total notes count
    notes_result = await db.execute(
        select(func.count(Note.id)).where(Note.user_id == current_user.id)
    )
    total_notes = notes_result.scalar_one()

    # 3. File type distribution
    type_result = await db.execute(
        select(Document.file_type, func.count(Document.id))
        .where(Document.user_id == current_user.id)
        .group_by(Document.file_type)
    )
    file_type_distribution = {}
    for ftype, count in type_result.all():
        # Clean type name
        clean_type = ftype.split("/")[-1].upper() if "/" in ftype else ftype.upper()
        file_type_distribution[clean_type] = count

    # 4. Top tags extraction (from JSON list in Postgres)
    # We can fetch notes and count tags in Python to ensure cross-database compatibility
    tags_result = await db.execute(
        select(Note.tags).where(Note.user_id == current_user.id, Note.tags != None)
    )
    tag_counts = {}
    for tags_list in tags_result.scalars().all():
        if isinstance(tags_list, list):
            for t in tags_list:
                tag_counts[t] = tag_counts.get(t, 0) + 1

    top_tags = [
        {"name": tag, "count": count}
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    ]

    # 5. Recent activity (latest uploaded papers)
    activity_result = await db.execute(
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(Document.uploaded_at.desc())
        .limit(5)
    )
    recent_activity = []
    for doc in activity_result.scalars().all():
        recent_activity.append({
            "id": str(doc.id),
            "event": "Uploaded paper",
            "detail": doc.title,
            "timestamp": doc.uploaded_at
        })

    return AnalyticsOverview(
        total_papers=total_papers,
        total_notes=total_notes,
        file_type_distribution=file_type_distribution,
        top_tags=top_tags,
        recent_activity=recent_activity
    )


@router.get(
    "/timeline",
    response_model=list[TimelineItem],
    summary="Get publication year timeline",
)
async def get_publication_timeline(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get uploaded documents ordered by publication year (if available in metadata).
    """
    result = await db.execute(
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(Document.uploaded_at.desc())
    )
    documents = result.scalars().all()
    
    timeline = []
    for doc in documents:
        # Try to extract year from metadata, fallback to upload year
        year = doc.uploaded_at.year
        if doc.metadata_ and isinstance(doc.metadata_, dict):
            year = doc.metadata_.get("year", year)
            try:
                year = int(year)
            except ValueError:
                pass
                
        timeline.append(
            TimelineItem(
                id=doc.id,
                title=doc.title,
                year=year,
                filename=doc.filename
            )
        )
        
    # Sort by year descending
    timeline.sort(key=lambda x: x.year, reverse=True)
    return timeline


@router.get(
    "/export/{document_id}",
    summary="Export research assets",
)
async def export_document_assets(
    document_id: uuid.UUID,
    format: str = Query("markdown", description="Format to export: markdown | text"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Export document abstract and user notes into a clean, downloadable text document.
    """
    # 1. Fetch document
    doc_result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    doc = doc_result.scalar_one_or_none()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    # 2. Fetch notes
    notes_result = await db.execute(
        select(Note)
        .where(Note.document_id == document_id, Note.user_id == current_user.id)
        .order_by(Note.page_number.asc().nulls_last())
    )
    notes = notes_result.scalars().all()

    # 3. Format text content
    export_io = io.StringIO()
    export_io.write(f"# RESEARCH WORKSPACE REPORT: {doc.title.upper()}\n")
    export_io.write(f"Source file: {doc.filename}\n")
    export_io.write(f"Generated at: {doc.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
    export_io.write("=" * 60 + "\n\n")

    export_io.write("## 1. ABSTRACT / SUMMARY\n")
    export_io.write(f"{doc.abstract or 'No abstract extracted.'}\n\n")

    export_io.write("## 2. ANNOTATIONS & NOTES\n")
    if not notes:
        export_io.write("No annotations recorded for this document.\n")
    else:
        for idx, note in enumerate(notes):
            page_ref = f"Page {note.page_number}" if note.page_number else "General Note"
            tags_ref = f" (Tags: {', '.join(note.tags)})" if note.tags else ""
            export_io.write(f"### Note #{idx+1} [{page_ref}]{tags_ref}\n")
            export_io.write(f"{note.content}\n\n")

    export_io.seek(0)
    
    # 4. Stream response file
    filename = f"export_{doc.id.hex}.md" if format == "markdown" else f"export_{doc.id.hex}.txt"
    media_type = "text/markdown" if format == "markdown" else "text/plain"

    return StreamingResponse(
        io.BytesIO(export_io.read().encode("utf-8")),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
