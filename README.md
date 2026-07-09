# 🧠 ResearchMind AI

### *The Elite AI-Powered Research Assistant Workspace*

<div align="center">


[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)

A production-ready, full-stack AI research workspace that enables academics and students to read, analyze, compare, and synthesize scientific papers using **Retrieval-Augmented Generation (RAG)**.

[Key Features](#-key-features) • [System Architecture](#-system-architecture) • [Technology Stack](#-technology-stack) • [Quick Start](#-quick-start) • [Developer Guides](#-developer-guides)

</div>

---

## ✨ Key Features

ResearchMind AI transforms how you interact with scientific literature. It incorporates several advanced systems:

### 📄 Intelligent Document Processing
* **Multi-format Parsing**: Upload academic papers in PDF, DOCX, TXT, or Markdown formats.
* **Page-Aware Processing**: PyMuPDF-based text extractor maps extracted text page-by-page, allowing exact reference citations.
* **Smart Chunking**: Recursive character text splitters slice text into 1,000-character segments with a 200-character overlap to preserve semantic context.

### 🤖 Advanced RAG & Multi-Tenant Q&A
* **Semantic Context Retrieval**: Uses local **Sentence Transformers** to convert queries and text chunks into dense vector spaces.
* **Tenant Isolation**: Embeddings are stored in **ChromaDB** with strict metadata filters matching the current `user_id` and `document_id`.
* **Citations & Confidence Scores**: Every response includes exact page references and semantic similarity scores.
* **Conversation Memory**: Remembers past user queries inside SQL-backed chat history.

### 📊 Scientific Research Workspace
* **Paper Comparison Matrix**: Compare multiple papers side-by-side on Methods, Datasets, Architectures, Results, Strengths, and Weaknesses.
* **Research Gap Finder**: Identifies methodology shortcuts, missing experiments, and future research scopes.
* **Academic Citation Generator**: Automatically extracts metadata to format citations in APA, MLA, IEEE, Chicago, and BibTeX.
* **Literature Review Builder**: Generates structured, Markdown-based related work syntheses.

### 📓 Notes & Knowledge Organization
* **Research Notebook**: Create annotations, stand-alone Markdown notes, and tag pages as you read.
* **Collections & Folders**: Categorize papers into custom collections.
* **Interactive Knowledge Graph**: Dynamic visualizer mapping authors, topics, and keywords into entity-relationship networks.
* **Analytics Dashboard**: Tracks reading metrics, top tag frequencies, file distribution, and recent workspace activity.

---

## 🏗️ System Architecture

ResearchMind AI splits operations across a high-speed asynchronous API backend and a responsive Single Page Application frontend:

```
ResearchMind AI
├── Frontend (React 19 + TypeScript 5)
│   ├── UI Layer (Tailwind CSS v4 + Framer Motion)
│   ├── State Store (Zustand)
│   └── API Service (Axios Client)
│
├── Backend (FastAPI + Python)
│   ├── Endpoint Routers (REST Controllers)
│   ├── Business Services (Extraction & Synthesis Logic)
│   ├── Vector Engine (Sentence Transformers + ChromaDB)
│   └── Database Layer (SQLAlchemy 2.0 Async ORM)
│
└── Storage
    ├── PostgreSQL (Users, Documents, Chat Logs, Notes)
    ├── ChromaDB (Vector Store)
    └── File Storage (Raw Uploads)
```

### The RAG Pipeline Workflow
```
[User Document] ──> PyMuPDF Parser ──> Text Chunks ──> Vector Embeddings ──> ChromaDB
                                                                                  │
[User Question] ──> Query Embedding ──> Similarity Match ──> Cited Prompt ──> LLM ──> Answer
```

---

## 🛠️ Technology Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | React 19, TypeScript 5, Vite | Modern rendering, type safety, and fast compilation |
| **Styling** | Tailwind CSS v4, Framer Motion | Glossmorphic themes, responsive layouts, and spring animations |
| **Backend** | FastAPI, Python 3.11+ | High-performance asynchronous REST API controllers |
| **ORM & DB** | SQLAlchemy 2.0 (Async), PostgreSQL 16 | Scalable structured database storage and migrations |
| **Vector DB** | ChromaDB, SQLite (`aiosqlite`) | Isolated multi-tenant semantic indexes and testing |
| **AI Agents** | LangChain, OpenAI-compatible APIs | Large Language Model synthesis and embedding generation |

---

## 🚀 Quick Start

### Prerequisites
Make sure you have [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed on your machine.

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Kaifali786/Researchmind-ai.git
   cd Researchmind-ai
   ```

2. **Configure Environment Variables**:
   Copy the example environment template and add your OpenAI API key:
   ```bash
   cp .env.example .env
   ```

3. **Start All Services**:
   Start the databases, backend API, and React frontend with a single command:
   ```bash
   docker-compose up --build -d
   ```

4. **Access the Platform**:
   * **Frontend Workspace**: [http://localhost:5173](http://localhost:5173)
   * **Interactive API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Testing & Linting

We maintain high code quality with continuous integration checks for type safety, lint compliance, and endpoint testing:

### Running Backend Unit Tests
Our tests run on a self-contained in-memory SQLite database for high speed:
```bash
cd backend
python -m pytest tests/ -v
```

### Running Code Lint Check
We use Ruff to verify python style conventions:
```bash
cd backend
ruff check app/
```

### Running Frontend Verification
Check for TypeScript compiler errors and static assets builds:
```bash
cd frontend
npm run build
npm run lint
```

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
Built with ❤️ by Muhammad Kaif
</div>
