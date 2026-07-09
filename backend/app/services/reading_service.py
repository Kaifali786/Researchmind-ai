from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.config import get_settings
from app.models.document import Document, DocumentChunk

settings = get_settings()


class ReadingService:
    """
    ReadingService handles AI reading features like summarization,
    paragraph explanation/simplification, key idea extraction,
    and structured bullet-point notes.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the ReadingService.

        Args:
            db: Async database session.
        """
        self.db = db
        
        # Setup LLM
        api_key = settings.OPENAI_API_KEY or "no-key-needed"
        self.llm = ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base=settings.OPENAI_API_BASE,
            model_name=settings.OPENAI_MODEL,
            temperature=0.3
        )

    async def _get_document_context(self, document_id: UUID, max_chunks: int = 5) -> str:
        """
        Helper method to retrieve the first few chunks of a document (typically abstract/introduction)
        to act as context for summary and key ideas extraction.
        """
        result = await self.db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
            .limit(max_chunks)
        )
        chunks = result.scalars().all()
        return "\n\n".join([c.content for c in chunks])

    async def summarize_document(self, document_id: UUID) -> str:
        """
        Generate a comprehensive executive summary of a document based on its initial sections.

        Args:
            document_id: UUID of the document.

        Returns:
            AI-generated summary string in Markdown.
        """
        context = await self._get_document_context(document_id, max_chunks=6)
        if not context:
            return "No document text content available to summarize."

        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an elite academic research summarization agent. "
                "Analyze the provided text from a research paper and write a clear, structured, "
                "and concise executive summary (in Markdown).\n\n"
                "Include:\n"
                "- **Background & Objective**: What problem does this paper address?\n"
                "- **Core Methodology**: How did the authors approach the problem?\n"
                "- **Key Findings/Results**: What are the main outcomes?\n"
                "- **Significance**: Why do these results matter?"
            )),
            ("human", "Text:\n{context}")
        ])

        chain = prompt | self.llm | StrOutputParser()
        return await chain.ainvoke({"context": context})

    async def extract_key_ideas(self, document_id: UUID) -> list[str]:
        """
        Extract the top 5 key ideas or contributions of the paper.

        Args:
            document_id: UUID of the document.

        Returns:
            A list of strings representing key ideas.
        """
        context = await self._get_document_context(document_id, max_chunks=6)
        if not context:
            return ["No document text content available to extract ideas."]

        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an academic analysis agent. "
                "Extract the top 5 most important key ideas, contributions, or takeaways "
                "from the provided text. Return them as a plain bulleted list. "
                "Do not include any intro or outro text. Start each line with a bullet (-) character."
            )),
            ("human", "Text:\n{context}")
        ])

        chain = prompt | self.llm | StrOutputParser()
        raw_output = await chain.ainvoke({"context": context})
        
        # Parse bullet points into list elements
        ideas = []
        for line in raw_output.split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("*"):
                ideas.append(line[1:].strip())
            elif line:
                # Fallback if markdown prefix is missing
                ideas.append(line)
                
        return ideas[:5]

    async def generate_bullet_notes(self, document_id: UUID) -> str:
        """
        Generate structured study/reading notes in bullet points from the paper.

        Args:
            document_id: UUID of the document.

        Returns:
            AI-generated bullet-point notes.
        """
        context = await self._get_document_context(document_id, max_chunks=6)
        if not context:
            return "No document text content available to generate notes."

        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an advanced study assistant. "
                "Generate structured, comprehensive reading notes in bullet-point format "
                "for the provided text. Organize them into clear headings (e.g. Introduction, "
                "Proposed Model, Experiments)."
            )),
            ("human", "Text:\n{context}")
        ])

        chain = prompt | self.llm | StrOutputParser()
        return await chain.ainvoke({"context": context})

    async def explain_text(self, text: str) -> str:
        """
        Simplify and explain a selected paragraph of text, defining any technical jargon.

        Args:
            text: Selected paragraph/text snippet.

        Returns:
            AI-generated simplified explanation.
        """
        if not text.strip():
            return "Please provide a non-empty text selection to explain."

        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an expert scientific translator. Your task is to explain the "
                "provided technical text snippet in simpler terms, making it accessible to a "
                "first-year student while preserving the scientific core. "
                "If there is complex jargon or mathematical concepts, define them clearly."
            )),
            ("human", "Snippet:\n{text}")
        ])

        chain = prompt | self.llm | StrOutputParser()
        return await chain.ainvoke({"text": text})
