<div align="center">

# 🧠 ResearchMind AI

### Intelligent Research Assistant Powered by AI

[![CI Pipeline](https://github.com/yourusername/researchmind-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/researchmind-ai/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)

*A production-ready AI research workspace that helps researchers and students read, understand, compare, and organize academic papers using Retrieval-Augmented Generation (RAG).*

[Features](#-features) · [Quick Start](#-quick-start) · [Architecture](#-architecture) · [Documentation](#-documentation) · [Contributing](#-contributing)

</div>

---

## ✨ Features

### 📄 Document Management
Upload and manage research papers in PDF, DOCX, TXT, Markdown, and ZIP formats with drag-and-drop support.

### 🤖 AI-Powered Reading
- **Paper Summarization** — Get concise summaries of entire papers or specific sections
- **Paragraph Explanation** — Simplify complex technical language instantly
- **Key Ideas Extraction** — Extract the most important concepts automatically
- **Bullet-Point Notes** — Generate structured notes from any paper

### 💬 Intelligent Q&A
Ask questions about uploaded papers and get precise answers with:
- Exact page and paragraph citations
- Confidence scores for every answer
- Follow-up question support with conversation memory

### 📊 Research Comparison
Compare multiple papers side-by-side across methods, datasets, models, results, strengths, weaknesses, and future work.

### 🔍 Research Gap Finder
Automatically identify missing experiments, open problems, future research opportunities, and unanswered questions.

### 📝 Citation Generator
Generate citations in APA, MLA, IEEE, Chicago, and BibTeX formats.

### 🕸️ Knowledge Graph
Interactive visualization of authors, topics, keywords, relationships, and citation networks.

### 🔎 Semantic Search
Search papers using meaning — not just keywords — powered by sentence embeddings.

### 📓 Research Notebook
Save notes, highlights, bookmarks, and tags while reading papers.

### 📖 Literature Review Generator
Automatically generate Introduction, Related Work, Discussion, and Conclusion sections.

### 📈 Analytics Dashboard
Track reading progress, most studied topics, keyword frequency, upload statistics, and citation metrics.

### 📤 Export
Export results as PDF, DOCX, or Markdown.

---

## 🛠️ Tech Stack

| Layer | Technologies |
|:---|:---|
| **Frontend** | React 19, TypeScript 5, Tailwind CSS v4, Framer Motion, shadcn/ui |
| **Backend** | FastAPI, Python 3.11+, SQLAlchemy 2.0, Alembic |
| **Database** | PostgreSQL 16, ChromaDB (Vector Store) |
| **AI/ML** | LangChain, Sentence Transformers, OpenAI-compatible API |
| **DevOps** | Docker, GitHub Actions CI/CD |

---

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- [Git](https://git-scm.com/)
- An OpenAI API key (or [Ollama](https://ollama.ai/) for local LLM)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/researchmind-ai.git
cd researchmind-ai

# Configure environment
cp .env.example .env
# Edit .env and add your API key

# Start all services
docker-compose up -d

# The application is now running:
# Frontend:  http://localhost:5173
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/docs
```

### Development Setup (Without Docker)

<details>
<summary>Backend</summary>

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
</details>

<details>
<summary>Frontend</summary>

```bash
cd frontend
npm install
npm run dev
```
</details>

---

## 🏗️ Architecture

```
ResearchMind AI
├── Frontend (React + TypeScript + Vite)
│   ├── UI Layer (shadcn/ui + Tailwind CSS)
│   ├── State Management (Zustand)
│   └── API Client (Axios + React Query)
│
├── Backend (FastAPI + Python)
│   ├── API Routes (RESTful)
│   ├── Service Layer (Business Logic)
│   ├── RAG Pipeline (LangChain)
│   ├── Embedding Service (Sentence Transformers)
│   └── Document Processor (PyMuPDF)
│
└── Storage
    ├── PostgreSQL (Users, Papers, Notes, History)
    ├── ChromaDB (Vector Embeddings)
    └── File Storage (Uploaded Documents)
```

### RAG Pipeline

```
Upload → Extract Text → Chunk → Embed → Store in ChromaDB
                                              ↓
Question → Embed → Similarity Search → Retrieve Context → LLM → Answer + Citations
```

---

## 📁 Project Structure

```
researchmind-ai/
├── .github/              # GitHub Actions, issue/PR templates
├── backend/
│   ├── app/
│   │   ├── api/          # API routes and dependencies
│   │   ├── core/         # Config, security, middleware
│   │   ├── db/           # Database setup and migrations
│   │   ├── models/       # SQLAlchemy models
│   │   ├── repositories/ # Data access layer
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── main.py       # FastAPI application
│   ├── tests/            # Backend tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Route pages
│   │   ├── store/        # Zustand stores
│   │   ├── lib/          # Utilities
│   │   └── types/        # TypeScript types
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## 📖 Documentation

| Document | Description |
|:---|:---|
| [Installation Guide](docs/installation.md) | Detailed setup instructions |
| [User Guide](docs/user-guide.md) | How to use ResearchMind AI |
| [API Documentation](http://localhost:8000/docs) | Interactive API docs (Swagger) |
| [Developer Guide](docs/developer-guide.md) | Architecture and development setup |
| [Deployment Guide](docs/deployment.md) | Production deployment instructions |

---

## 🔒 Security

- JWT authentication with bcrypt password hashing
- Input validation on all endpoints (Pydantic)
- SQL injection protection (SQLAlchemy ORM)
- XSS/CSRF protection
- Rate limiting on sensitive endpoints
- CORS configuration

---

## 🧪 Testing

```bash
# Backend tests
cd backend && pytest tests/ --cov=app -v

# Frontend tests
cd frontend && npm run test

# E2E tests
cd frontend && npx playwright test
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built with ❤️ by Muhammad Kaif

**[⬆ Back to Top](#-researchmind-ai)**

</div>
