import os
import traceback
from datetime import datetime, timezone
from uuid import UUID

import fitz  # PyMuPDF
import docx  # python-docx
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentStatus, DocumentChunk
from app.repositories.document_repo import DocumentRepository

class DocumentService:
    """
    Service responsible for document ingestion, text parsing,
    chunking, and metadata extraction.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the DocumentService.

        Args:
            db: Async database session.
        """
        self.db = db
        self.doc_repo = DocumentRepository(db)

    async def process_document(self, document_id: UUID) -> None:
        """
        Ingest and process an uploaded document in the background.

        This parses the raw text (using PyMuPDF for PDFs, python-docx for DOCX,
        or direct reads for TXT/MD), splits it into pages and character-based
        overlapping chunks, and persists them for vector database search.

        Args:
            document_id: UUID of the document to process.
        """
        # Fetch the document
        doc = await self.doc_repo.get_by_id(document_id)
        if not doc:
            print(f"Error: Document {document_id} not found in database.")
            return

        # Set status to processing
        doc.status = DocumentStatus.PROCESSING
        await self.db.commit()

        try:
            file_path = doc.file_path
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Physical file not found at {file_path}")

            file_ext = os.path.splitext(doc.filename)[1].lower()
            chunks_to_create = []
            page_count = 0

            # Text splitter setup
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )

            # ── 1. PDF Parsing (Page-by-page text extraction) ─────────────────
            if file_ext == '.pdf':
                # Open PDF via PyMuPDF
                pdf_doc = fitz.open(file_path)
                page_count = len(pdf_doc)
                doc.page_count = page_count
                
                chunk_index = 0
                for page_num in range(page_count):
                    page = pdf_doc.load_page(page_num)
                    page_text = page.get_text("text").strip()
                    
                    if not page_text:
                        continue
                    
                    # Split page text into chunks
                    splits = text_splitter.split_text(page_text)
                    for split in splits:
                        chunks_to_create.append(
                            DocumentChunk(
                                document_id=doc.id,
                                chunk_index=chunk_index,
                                content=split,
                                page_number=page_num + 1,  # 1-indexed page
                                section=None
                            )
                        )
                        chunk_index += 1
                pdf_doc.close()

            # ── 2. DOCX Parsing ──────────────────────────────────────────────
            elif file_ext == '.docx':
                docx_doc = docx.Document(file_path)
                # Combine paragraph text
                full_text = "\n".join([p.text for p in docx_doc.paragraphs if p.text.strip()])
                page_count = 1
                doc.page_count = page_count

                splits = text_splitter.split_text(full_text)
                for idx, split in enumerate(splits):
                    chunks_to_create.append(
                        DocumentChunk(
                            document_id=doc.id,
                            chunk_index=idx,
                            content=split,
                            page_number=1,
                            section=None
                        )
                    )

            # ── 3. Text & Markdown Parsing ────────────────────────────────────
            elif file_ext in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    full_text = f.read().strip()
                
                page_count = 1
                doc.page_count = page_count

                splits = text_splitter.split_text(full_text)
                for idx, split in enumerate(splits):
                    chunks_to_create.append(
                        DocumentChunk(
                            document_id=doc.id,
                            chunk_index=idx,
                            content=split,
                            page_number=1,
                            section=None
                        )
                    )
            
            else:
                raise ValueError(f"Unsupported file extension for parsing: {file_ext}")

            # Persist document chunks to database
            if chunks_to_create:
                self.db.add_all(chunks_to_create)

            # Update document stats and metadata
            doc.status = DocumentStatus.COMPLETED
            doc.processed_at = datetime.now(timezone.utc)
            if doc.metadata_ is None:
                doc.metadata_ = {}
            doc.metadata_["total_chunks"] = len(chunks_to_create)
            
            await self.db.commit()

            # ── Vector DB Indexing (ChromaDB) ────────────────────────────────
            from app.services.rag_service import RAGService
            try:
                rag_service = RAGService(self.db)
                await rag_service.index_document_chunks(doc.id, doc.user_id)
                print(f"Successfully indexed document {doc.title} inside ChromaDB.")
            except Exception as vector_err:
                print(f"WARNING: Database storage succeeded but ChromaDB vector indexing failed: {vector_err}")

            print(f"Successfully processed document {doc.title} into {len(chunks_to_create)} chunks.")


        except Exception as e:
            # Rollback active transactions and update status to failed
            await self.db.rollback()
            tb = traceback.format_exc()
            print(f"Failed to process document {document_id}: {e}\n{tb}")
            
            doc.status = DocumentStatus.FAILED
            doc.processed_at = datetime.now(timezone.utc)
            if doc.metadata_ is None:
                doc.metadata_ = {}
            doc.metadata_["error"] = str(e)
            doc.metadata_["traceback"] = tb
            
            await self.db.commit()
