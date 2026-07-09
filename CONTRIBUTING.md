# Contributing to ResearchMind AI

Thank you for your interest in contributing to ResearchMind AI! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](../../issues)
2. If not, create a new issue using the bug report template
3. Include as much detail as possible:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Screenshots if applicable
   - Environment details

### Suggesting Features

1. Check existing [feature requests](../../issues?q=label%3Aenhancement)
2. Create a new issue using the feature request template
3. Describe the feature and its use case

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes following our coding standards
4. Write tests for new functionality
5. Ensure all tests pass
6. Commit with clear messages: `git commit -m "feat: add paper comparison view"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/researchmind-ai.git
cd researchmind-ai

# Copy environment configuration
cp .env.example .env

# Start all services
docker-compose up -d

# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Coding Standards

### Python (Backend)
- Follow PEP 8
- Use type hints for all function signatures
- Write docstrings for all public functions
- Use `ruff` for linting
- Use `black` for formatting

### TypeScript (Frontend)
- Use strict TypeScript (no `any`)
- Follow React best practices
- Use functional components with hooks
- Use meaningful component and variable names

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation
- `style:` — Formatting (no code change)
- `refactor:` — Code restructuring
- `test:` — Adding tests
- `chore:` — Maintenance

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
