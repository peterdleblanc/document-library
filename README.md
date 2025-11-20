# Document Library System

A comprehensive document management system with AI-powered classification, full-text search, version control, and audit trails.

## Features

- **Smart Document Classification** - AI-powered auto-tagging and categorization using Claude
- **Full-Text Search** - Search document titles AND contents (PDFs, Word docs, images)
- **OCR Support** - Extract text from scanned documents and images
- **Version Control** - Track all document versions with visual/text diffs
- **Audit Trail** - Complete logging of all user actions
- **Metadata Extraction** - Automatic metadata generation and search
- **Background Processing** - Async processing with real-time progress updates

## Technology Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL 16+ (metadata, users, audit)
- **Storage:** MinIO (S3-compatible object storage)
- **Search:** Meilisearch (full-text search)
- **Vector DB:** pgvector (semantic search)
- **Queue:** Celery + Redis (background jobs)
- **AI:** Claude 3.5 Sonnet (metadata generation)
- **OCR:** Tesseract + AWS Textract

### Frontend
- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **State Management:** React Query + Context API
- **UI Library:** TailwindCSS + shadcn/ui
- **Forms:** React Hook Form + Zod

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd document-library
   ```

2. **Start infrastructure services**
   ```bash
   docker-compose up -d
   ```

   This starts:
   - PostgreSQL (port 5432)
   - MinIO (port 9000, console: 9001)
   - Redis (port 6379)
   - Meilisearch (port 7700)
   - PgAdmin (port 5050)

3. **Set up backend**
   ```bash
   cd backend

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Copy environment file and configure
   cp .env.example .env
   # Edit .env with your settings

   # Run database migrations
   alembic upgrade head

   # Start development server
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Set up frontend**
   ```bash
   cd frontend

   # Install dependencies
   npm install

   # Start development server
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - MinIO Console: http://localhost:9001
   - PgAdmin: http://localhost:5050

## Project Structure

```
document-library/
├── backend/
│   ├── alembic/              # Database migrations
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/    # API route handlers
│   │   │   └── dependencies.py
│   │   ├── core/             # Core functionality
│   │   ├── db/               # Database configuration
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   └── utils/            # Utilities
│   ├── tests/                # Tests
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── hooks/            # Custom hooks
│   │   ├── services/         # API services
│   │   ├── types/            # TypeScript types
│   │   └── utils/            # Utilities
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
└── README.md
```

## Development Roadmap

### Phase 1: Core Infrastructure (Weeks 1-4) ✓
- [x] Backend project structure
- [x] Database models and migrations
- [x] Authentication (JWT)
- [ ] Basic file upload/download
- [ ] Document list UI

### Phase 2: Document Processing (Weeks 5-8)
- [ ] Text extraction (Apache Tika)
- [ ] OCR integration (Tesseract)
- [ ] Background job processing
- [ ] Progress tracking

### Phase 3: Search & AI (Weeks 9-12)
- [ ] Meilisearch integration
- [ ] Claude AI metadata generation
- [ ] Semantic search (pgvector)
- [ ] Search UI

### Phase 4: Version Control & Audit (Weeks 13-16)
- [ ] Document versioning
- [ ] Diff implementation
- [ ] Audit logging
- [ ] Version history UI

### Phase 5: Polish & Deploy (Weeks 17-20)
- [ ] Performance optimization
- [ ] Admin dashboard
- [ ] Security hardening
- [ ] Production deployment

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

## Contributing

This is a personal project. Feel free to fork and adapt for your needs.

## License

MIT License - See LICENSE file for details

## Environment Variables

See `backend/.env.example` for all available configuration options.

## Support

For issues and questions, please open an issue on GitHub.
