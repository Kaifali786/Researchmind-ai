import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.models.document import Document, DocumentChunk

settings = get_settings()


class PaperDetailsSchema(BaseModel):
    title: str = Field(description="Title of the paper")
    methods: str = Field(description="Summary of methodology used")
    datasets: str = Field(description="Datasets referenced or used")
    models: str = Field(description="Models or architectures proposed")
    results: str = Field(description="Main findings or results")
    strengths: str = Field(description="Key strengths of the paper")
    weaknesses: str = Field(description="Key limitations or weaknesses")


class CitationSchema(BaseModel):
    authors: str = Field(description="Comma-separated list of authors, e.g. Vaswani, A., Shazeer, N.")
    year: str = Field(description="Publication year, e.g. 2017")
    title: str = Field(description="Title of the paper")
    journal: str = Field(description="Journal or conference name, e.g. Advances in Neural Information Processing Systems")
    volume: str = Field(description="Volume number, or N/A")
    pages: str = Field(description="Page range, or N/A")
    publisher: str = Field(description="Publisher or institution, or N/A")


class ResearchService:
    """
    ResearchService implements core research workspace tools like paper comparisons,
    citation formatting, literature review synthesis, and research gap finding.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the ResearchService.

        Args:
            db: Async database session.
        """
        self.db = db
        
        api_key = settings.OPENAI_API_KEY or "no-key-needed"
        self.llm = ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base=settings.OPENAI_API_BASE,
            model_name=settings.OPENAI_MODEL,
            temperature=0.2
        )

    async def _get_first_chunks(self, document_id: uuid.UUID, max_chunks: int = 5) -> str:
        """Helper to get initial document text for analysis."""
        result = await self.db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
            .limit(max_chunks)
        )
        chunks = result.scalars().all()
        return "\n\n".join([c.content for c in chunks])

    async def compare_papers(self, document_ids: list[uuid.UUID]) -> list[dict]:
        """
        Extract key details from multiple papers and compile a side-by-side comparison matrix.

        Args:
            document_ids: List of document UUIDs.

        Returns:
            A list of compared paper details dictionary items.
        """
        comparison_matrix = []

        for doc_id in document_ids:
            # Fetch document
            result = await self.db.execute(select(Document).where(Document.id == doc_id))
            doc = result.scalar_one_or_none()
            if not doc:
                continue

            # Get text context
            context = await self._get_first_chunks(doc_id, max_chunks=5)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", (
                    "You are a scientific analysis expert. Extract structured information from the provided "
                    "research paper text. Format the output in JSON matching the schema.\n"
                    "If a detail is not present in the text, use 'Not mentioned'."
                )),
                ("human", "Text:\n{context}")
            ])

            parser = JsonOutputParser(pydantic_object=PaperDetailsSchema)
            chain = prompt | self.llm | parser

            try:
                extracted = await chain.ainvoke({"context": context})
                # Add document metadata
                extracted["id"] = str(doc_id)
                extracted["filename"] = doc.filename
                comparison_matrix.append(extracted)
            except Exception as e:
                print(f"Error comparing paper {doc_id}: {e}")
                # Fallback item
                comparison_matrix.append({
                    "id": str(doc_id),
                    "title": doc.title,
                    "filename": doc.filename,
                    "methods": "Error extracting methodology.",
                    "datasets": "N/A",
                    "models": "N/A",
                    "results": "N/A",
                    "strengths": "N/A",
                    "weaknesses": "N/A"
                })

        return comparison_matrix

    async def identify_research_gaps(self, document_id: uuid.UUID) -> dict:
        """
        Automatically analyze a paper's text to find open problems, limitations, and future research gaps.

        Args:
            document_id: UUID of the target document.

        Returns:
            Dictionary with categorized research gaps.
        """
        context = await self._get_first_chunks(document_id, max_chunks=7)
        if not context:
            return {"gaps": ["No text content available to parse."]}

        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an academic reviewer. Analyze the provided research paper text and identify:\n"
                "1. Missing experiments / evaluation gaps.\n"
                "2. Open problems or unresolved questions.\n"
                "3. Limitations acknowledged by the authors.\n"
                "4. Future research opportunities.\n\n"
                "Provide a detailed, structured analysis in Markdown format."
            )),
            ("human", "Text:\n{context}")
        ])

        chain = prompt | self.llm | StrOutputParser()
        analysis = await chain.ainvoke({"context": context})
        return {"analysis": analysis}

    async def generate_citations(self, document_id: uuid.UUID) -> dict:
        """
        Generate academic citations for a document in APA, MLA, IEEE, Chicago, and BibTeX.

        Args:
            document_id: UUID of the document.

        Returns:
            Dictionary containing formatted citation strings.
        """
        result = await self.db.execute(select(Document).where(Document.id == document_id))
        doc = result.scalar_one_or_none()
        if not doc:
            return {}

        # Attempt to extract metadata from initial chunks
        context = await self._get_first_chunks(document_id, max_chunks=3)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an academic citations metadata extractor. "
                "Extract the citation fields (authors, year, title, journal/conference, "
                "volume, pages, publisher) from the document header text. "
                "Return a JSON object conforming to the schema.\n"
                "If volume/pages/publisher are missing, set to 'N/A'."
            )),
            ("human", "Text:\n{context}")
        ])

        parser = JsonOutputParser(pydantic_object=CitationSchema)
        chain = prompt | self.llm | parser

        try:
            meta = await chain.ainvoke({"context": context})
        except Exception:
            # Fallback metadata
            meta = {
                "authors": "Unknown",
                "year": str(doc.uploaded_at.year),
                "title": doc.title,
                "journal": "N/A",
                "volume": "N/A",
                "pages": "N/A",
                "publisher": "N/A"
            }

        authors = meta.get("authors", "Unknown")
        year = meta.get("year", "N/A")
        title = meta.get("title", doc.title)
        journal = meta.get("journal", "N/A")
        volume = meta.get("volume", "N/A")
        pages = meta.get("pages", "N/A")
        publisher = meta.get("publisher", "N/A")

        # Format Authors for IEEE (Initials + Last Name)
        ieee_authors = authors
        # Format Authors for BibTeX Key (FirstAuthorYear)
        first_author = authors.split(",")[0].split(" ")[0].strip()
        bib_key = f"{first_author.lower()}{year}"

        # ── Format Templates ─────────────────────────────────────────
        apa = f"{authors} ({year}). {title}. *{journal}*."
        if volume != "N/A":
            apa += f" {volume}."
        if pages != "N/A":
            apa += f" {pages}."

        mla = f"{authors}. \"{title}.\" *{journal}*, vol. {volume}, {year}, pp. {pages}."
        
        ieee = f"{ieee_authors}, \"{title},\" *{journal}*, vol. {volume}, pp. {pages}, {year}."
        
        chicago = f"{authors}. \"{title}.\" *{journal}* {volume} ({year}): {pages}."

        bibtex = (
            f"@article{{{bib_key},\n"
            f"  author    = {{{authors}}},\n"
            f"  title     = {{{title}}},\n"
            f"  journal   = {{{journal}}},\n"
            f"  year      = {{{year}}},\n"
            f"  volume    = {{{volume}}},\n"
            f"  pages     = {{{pages}}},\n"
            f"  publisher = {{{publisher}}}\n"
            f"}}"
        )

        return {
            "apa": apa,
            "mla": mla,
            "ieee": ieee,
            "chicago": chicago,
            "bibtex": bibtex
        }

    async def generate_literature_review(self, document_ids: list[uuid.UUID]) -> str:
        """
        Cohesively synthesize multiple research papers into an academic Literature Review.

        Args:
            document_ids: List of document UUIDs.

        Returns:
            Cohesive literature review string in Markdown.
        """
        paper_summaries = []

        for doc_id in document_ids:
            result = await self.db.execute(select(Document).where(Document.id == doc_id))
            doc = result.scalar_one_or_none()
            if not doc:
                continue

            context = await self._get_first_chunks(doc_id, max_chunks=3)
            paper_summaries.append(f"Paper: {doc.title}\nContext Snippet:\n{context}")

        if not paper_summaries:
            return "No documents selected to generate a literature review."

        combined_papers = "\n\n===\n\n".join(paper_summaries)

        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an academic research reviewer. Write a high-quality, professional Literature Review "
                "synthesizing the provided research papers.\n\n"
                "Your review should be written in an academic tone and formatted in Markdown with the following sections:\n"
                "1. **Introduction**: Introduce the research area and the relevance of the analyzed papers.\n"
                "2. **Synthesis of Methodologies**: Compare and contrast the different approaches, datasets, and architectures.\n"
                "3. **Discussion & Themes**: Analyze recurring themes, findings, strengths, and weaknesses across the papers.\n"
                "4. **Conclusion & Future Directions**: Summarize the takeaways and state the current research gaps."
            )),
            ("human", "Papers for Synthesis:\n{papers}")
        ])

        chain = prompt | self.llm | StrOutputParser()
        return await chain.ainvoke({"papers": combined_papers})

    async def extract_knowledge_graph(self, document_id: uuid.UUID) -> dict:
        """
        Extract key authors, topics, and keywords from the paper text
        to represent them as network nodes and links.
        """
        context = await self._get_first_chunks(document_id, max_chunks=3)
        if not context:
            return {"nodes": [], "links": []}

        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an academic network graph extraction agent. Analyze the provided research paper text "
                "and extract:\n"
                "1. Important authors (last names, e.g. Vaswani).\n"
                "2. The primary research topics/themes.\n"
                "3. Key methodologies/keywords (e.g. Self-Attention).\n\n"
                "Return ONLY a valid JSON object matching this structure (no formatting outside the JSON):\n"
                "{{\n"
                "  \"nodes\": [\n"
                "    {{ \"id\": \"string-id\", \"label\": \"Display Name\", \"type\": \"author\" | \"topic\" | \"keyword\" }}\n"
                "  ],\n"
                "  \"links\": [\n"
                "    {{ \"source\": \"string-id-1\", \"target\": \"string-id-2\", \"type\": \"author_of\" | \"discusses\" | \"utilizes\" }}\n"
                "  ]\n"
                "}}"
            )),
            ("human", "Text:\n{context}")
        ])

        try:
            chain = prompt | self.llm | JsonOutputParser()
            res = await chain.ainvoke({"context": context})
            return res
        except Exception as e:
            print(f"Error extracting knowledge graph for {document_id}: {e}")
            return {"nodes": [], "links": []}

