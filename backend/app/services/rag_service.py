import os
from uuid import UUID

import chromadb
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.document import Document, DocumentChunk
from app.models.chat import ChatSession, ChatMessage

settings = get_settings()


class RAGService:
    """
    RAG (Retrieval-Augmented Generation) Service.

    Coordinates document vector indexing in ChromaDB, context retrieval,
    semantic search, and LLM text generation with citations.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the RAGService.

        Args:
            db: Async database session.
        """
        self.db = db
        
        # Setup Embeddings
        # Uses OpenAI-compatible endpoints (supports OpenAI API or local Ollama)
        api_key = settings.OPENAI_API_KEY or "no-key-needed"
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=api_key,
            openai_api_base=settings.OPENAI_API_BASE,
            model="text-embedding-3-small"
        )

        # Setup persistent ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.vector_store = Chroma(
            client=self.chroma_client,
            collection_name="researchmind_corpus",
            embedding_function=self.embeddings
        )

    async def index_document_chunks(self, document_id: UUID, user_id: UUID) -> None:
        """
        Index all chunks of a document into ChromaDB.

        Args:
            document_id: UUID of the document.
            user_id: UUID of the owning user.
        """
        # Fetch chunks from Postgres database
        result = await self.db.execute(
            select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        )
        chunks = result.scalars().all()
        if not chunks:
            return

        texts = [c.content for c in chunks]
        metadatas = [
            {
                "document_id": str(document_id),
                "user_id": str(user_id),
                "page_number": c.page_number or 1,
                "chunk_index": c.chunk_index
            }
            for c in chunks
        ]
        ids = [str(c.id) for c in chunks]

        # Add to ChromaDB vector store
        self.vector_store.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids
        )

    async def answer_question(
        self,
        user_id: UUID,
        question: str,
        document_id: UUID | None = None
    ) -> dict:
        """
        Retrieve relevant document context and generate a cited response.

        Args:
            user_id: UUID of the asking user.
            question: The natural language question.
            document_id: Optional document UUID to limit search scope.

        Returns:
            A dictionary containing the generated answer, confidence score,
            and list of citations.
        """
        # ── 1. Retrieval (Semantic search over indexed chunks) ─────────────
        # Define metadata filters to ensure strict multi-tenant isolation
        search_filter = {"user_id": str(user_id)}
        if document_id:
            search_filter["document_id"] = str(document_id)

        # Retrieve top K similar chunks
        retrieved_docs = self.vector_store.similarity_search(
            query=question,
            k=5,
            filter=search_filter
        )

        if not retrieved_docs:
            return {
                "answer": "No reference context found. Please ensure you have uploaded documents first.",
                "confidence_score": 0.0,
                "citations": []
            }

        # ── 2. Format Context & Citations ────────────────────────────────
        context_parts = []
        citations = []
        
        for idx, doc in enumerate(retrieved_docs):
            page = doc.metadata.get("page_number", 1)
            doc_id = doc.metadata.get("document_id")
            
            # Format context block with citation tags
            context_parts.append(
                f"[Source {idx+1}] (Page {page}):\n{doc.page_content}"
            )
            
            citations.append({
                "source_index": idx + 1,
                "page": page,
                "snippet": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            })

        context_str = "\n\n".join(context_parts)

        # ── 3. Generation (LLM Synthesis) ──────────────────────────────
        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an elite academic research assistant. Analyze the provided context "
                "from the user's uploaded research papers and answer the question.\n\n"
                "Strict Guidelines:\n"
                "1. Your answer must be factual and directly supported by the context.\n"
                "2. If the context does not contain enough information to answer, state clearly: "
                "\"I cannot find sufficient information in the uploaded documents to answer this question.\"\n"
                "3. Format your response with clear academic tone and markdown.\n"
                "4. Cite your sources using [Source X] corresponding to the context tags (e.g., [Source 1])."
            )),
            ("human", "Context:\n{context}\n\nQuestion: {question}")
        ])

        api_key = settings.OPENAI_API_KEY or "no-key-needed"
        llm = ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base=settings.OPENAI_API_BASE,
            model_name=settings.OPENAI_MODEL,
            temperature=0.0
        )

        chain = prompt | llm | StrOutputParser()
        
        try:
            answer = await chain.ainvoke({"context": context_str, "question": question})
            # Estimate confidence based on semantic relevance / search match (heuristic)
            confidence = 0.95 if len(retrieved_docs) >= 3 else 0.75
        except Exception as e:
            answer = f"Error generating answer: {str(e)}"
            confidence = 0.0

        return {
            "answer": answer,
            "confidence_score": confidence,
            "citations": citations
        }
