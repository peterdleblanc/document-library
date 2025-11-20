# Document Library - Project Status

**Last Updated:** 2025-11-19
**Repository:** https://github.com/peterdleblanc/document-library

## Current Status: Phase 2 Complete ✅

### What's Working

#### 🔐 Authentication & User Management
- User registration and login (JWT tokens)
- Default admin user: `admin@admin.com` / `admin`
- Bcrypt password hashing (direct bcrypt, not passlib)
- Role-based access control ready

#### 📁 Document Management
- File upload to MinIO S3-compatible storage
- Document metadata in PostgreSQL
- Version tracking (v1 created on upload)
- File hash calculation for duplicate detection
- Download functionality (streaming and presigned URLs)
- Delete with cascade to MinIO

#### 🔄 Background Processing
- Celery workers processing documents asynchronously
- Redis-based task queue
- Real-time progress tracking (0-100%)
- Status updates (pending → processing → completed/failed)

#### 📝 Text Extraction (Phase 2 - NEW)
- **Apache Tika** integration for multi-format text extraction
  - PDF, Word (.doc/.docx), Excel, PowerPoint
  - HTML, RTF, plain text
  - Automatic MIME type detection
- **Tesseract OCR** for image-based documents
  - Standalone images (PNG, JPG, etc.)
  - Scanned PDFs (page-by-page conversion)
  - Automatic OCR detection (triggers on images or low-text PDFs)
- Extracted text stored in `document_text` table

#### 🗄️ Database Schema Management
- Complete SQL schema in `backend/init_db.sql`
- Database reset script: `./backend/reset_db.sh`
- Git pre-commit hook enforces model/SQL synchronization
- 8 tables: users, tags, documents, document_versions, document_text, document_metadata, document_embeddings, audit_logs

#### 🐳 Infrastructure
- Fully containerized with Docker Compose
- All services running and healthy:
  - nginx (reverse proxy, port 8080)
  - frontend (React + Vite, port 8173)
  - backend (FastAPI, port 8800)
  - celery-worker (background jobs)
  - postgres (port 5433)
  - redis (ports 6379, 6380)
  - minio (ports 9000, 9001)
  - meilisearch (port 7700)

### Recent Changes (Today)

#### Environment Setup
- Removed Podman, using Docker exclusively
- Docker version: 27.5.1
- Docker Compose version: 2.32.4
- All commands use `sudo docker compose`

#### Bug Fixes
1. **Bcrypt Password Hashing** - Fixed 72-byte truncation issue (backend/app/core/security.py:11)
2. **SQLAlchemy Reserved Keyword** - Renamed `metadata` to `doc_metadata` (backend/app/models/document.py:34)
3. **Frontend API URLs** - Fixed double `/api` prefix (frontend/src/services/api.ts)
4. **Nginx Configuration** - Fixed frontend port from 80 → 5173 (nginx/nginx.conf:3)

#### New Services
1. **Text Extraction Service** - `backend/app/services/text_extraction_service.py`
2. **OCR Service** - `backend/app/services/ocr_service.py`
3. **Enhanced Document Processing** - `backend/app/tasks/document_tasks.py`

## Phase Progress

### ✅ Phase 1: Core Infrastructure (COMPLETE)
- [x] Fully containerized architecture
- [x] Backend API with authentication
- [x] Frontend with login/register
- [x] Database models
- [x] Docker Compose setup

### ✅ Phase 2: Document Processing (COMPLETE)
- [x] File upload to MinIO
- [x] Text extraction (Apache Tika)
- [x] OCR integration (Tesseract)
- [x] Background job processing
- [x] Progress tracking

### 🔜 Phase 3: Search & AI (NEXT)
- [ ] Meilisearch integration
- [ ] Claude AI metadata generation
- [ ] Semantic search (pgvector)
- [ ] Advanced search UI

### 🔜 Phase 4: Version Control & Audit
- [ ] Document versioning UI
- [ ] Diff implementation
- [ ] Comprehensive audit logging
- [ ] Version history UI

### 🔜 Phase 5: Production Ready
- [ ] Performance optimization
- [ ] Admin dashboard
- [ ] Monitoring (Prometheus/Grafana)
- [ ] CI/CD pipeline

## Technical Stack

### Frontend
- React 18 + TypeScript
- Vite (dev server on port 5173)
- TailwindCSS
- Axios for API calls

### Backend
- FastAPI (Python 3.11)
- SQLAlchemy (async ORM)
- PostgreSQL 16
- MinIO (S3-compatible storage)
- Redis (cache & queue)
- Celery (background jobs)

### Text Processing
- Apache Tika 2.6.0 (text extraction)
- Tesseract OCR (image text extraction)
- Pillow 10.2.0 (image processing)
- pdf2image 1.17.0 (PDF → images)

### Future Integrations
- Meilisearch (full-text search)
- Claude 3.5 Sonnet (AI metadata)
- pgvector (semantic search)

## Important Commands

### Start Everything
```bash
sudo docker compose up -d
```

### Reset Database
```bash
./backend/reset_db.sh
```

### View Logs
```bash
# All services
sudo docker compose logs -f

# Specific service
sudo docker compose logs -f backend
sudo docker compose logs -f celery-worker
```

### Rebuild Containers
```bash
# Rebuild all
sudo docker compose up -d --build

# Rebuild specific service
sudo docker compose up -d --build backend
```

### Access Application
- Main app: http://localhost:8080
- API docs: http://localhost:8080/docs
- MinIO console: http://localhost:9001
- Backend direct: http://localhost:8800
- Frontend direct: http://localhost:8173

### Database Access
```bash
# Interactive shell
sudo docker compose exec postgres psql -U doclib -d document_library

# Run query
sudo docker compose exec postgres psql -U doclib -d document_library -c "SELECT * FROM users;"

# List tables
sudo docker compose exec postgres psql -U doclib -d document_library -c "\dt"
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│        NGINX Reverse Proxy (Port 8080)                  │
│    Routes: / → Frontend, /api → Backend                 │
└────────────┬─────────────────────────────┬──────────────┘
             │                             │
    ┌────────▼────────┐          ┌────────▼────────┐
    │   Frontend      │          │    Backend      │
    │   (React)       │          │   (FastAPI)     │
    │   Port 8173     │          │   Port 8800     │
    └─────────────────┘          └────────┬────────┘
                                          │
                                 ┌────────▼────────┐
                                 │  Celery Worker  │
                                 │  (Processing)   │
                                 └────────┬────────┘
                                          │
         ┌────────────────────────────────┼──────────────────┐
         │                                │                  │
    ┌────▼──────┐  ┌──────────┐  ┌───────▼────┐  ┌─────────▼──────┐
    │PostgreSQL │  │  MinIO   │  │   Redis    │  │  Meilisearch   │
    │  5433     │  │9000/9001 │  │ 6379/6380  │  │     7700       │
    └───────────┘  └──────────┘  └────────────┘  └────────────────┘
```

## Document Processing Flow

1. **Upload** (frontend) → POST /api/v1/documents/upload
2. **Save to MinIO** → `documents/{year}/{month}/{doc_id}/v{version}.ext`
3. **Create DB record** → documents table + document_versions table
4. **Queue background job** → Celery task `process_document`
5. **Download from MinIO** → Get file bytes
6. **Extract text** → Apache Tika
7. **Apply OCR if needed** → Tesseract (images or scanned PDFs)
8. **Store text** → document_text table
9. **Update status** → processing_status = "completed", progress = 100%

## Known Issues

### None Currently

All major issues from previous sessions have been resolved:
- ✅ Bcrypt password hashing working
- ✅ Frontend API URLs fixed
- ✅ Database schema synchronized
- ✅ Document upload working
- ✅ Text extraction working
- ✅ OCR processing working

## Development Workflow

### Making Schema Changes

1. Edit SQLAlchemy models in `backend/app/models/`
2. Update `backend/init_db.sql` with SQL changes
3. Test: `./backend/reset_db.sh`
4. Commit both files together (pre-commit hook will warn if out of sync)

### Adding New Features

1. Create service in `backend/app/services/`
2. Add API endpoint in `backend/app/api/`
3. Update frontend in `frontend/src/`
4. Test locally
5. Commit and push

### Hot Reload

Both frontend and backend support hot reload:
- Edit files in `frontend/src/` → instant refresh
- Edit files in `backend/app/` → auto-reload

## Next Steps (Phase 3)

### Priority 1: Search Integration
- [ ] Set up Meilisearch indexes
- [ ] Index documents on upload
- [ ] Create search API endpoint
- [ ] Build search UI in frontend

### Priority 2: AI Metadata Generation
- [ ] Add Anthropic API key to .env
- [ ] Create AI service for Claude integration
- [ ] Generate metadata: summary, categories, auto-tags
- [ ] Store in document_metadata table

### Priority 3: Semantic Search
- [ ] Enable pgvector extension
- [ ] Generate embeddings for chunks
- [ ] Store in document_embeddings table
- [ ] Implement similarity search API

## Files to Review Tomorrow

### Core Processing Logic
- `backend/app/tasks/document_tasks.py` - Main processing pipeline
- `backend/app/services/text_extraction_service.py` - Tika integration
- `backend/app/services/ocr_service.py` - Tesseract integration

### Database
- `backend/init_db.sql` - Complete schema
- `backend/app/models/document.py` - Document models

### API
- `backend/app/api/v1/documents.py` - Document endpoints
- `frontend/src/services/api.ts` - API client

## Git Repository

**URL:** https://github.com/peterdleblanc/document-library
**Branch:** master
**Last Commit:** feat: Phase 2 - Text extraction and OCR processing

### Commit History
1. Initial commit: Document Library System
2. Complete Docker containerization
3. Document upload/download with MinIO
4. Fix ports to browser-safe ranges
5. **Phase 2 - Text extraction and OCR** (current)

## Environment Notes

- **OS:** Kali Linux 6.16.8
- **Docker:** Running with sudo (user in docker group but needs relogin)
- **Containers:** All using multi-stage builds (dev target)
- **Volumes:** Persistent data for postgres, minio, redis, meilisearch

## Quick Test Checklist

✅ All services running: `sudo docker compose ps`
✅ Login works: http://localhost:8080 (admin@admin.com / admin)
✅ Upload document: Works and triggers processing
✅ View logs: `sudo docker compose logs -f celery-worker`
✅ Database query: `sudo docker compose exec postgres psql -U doclib -d document_library -c "\dt"`

## Ready for Tomorrow

Everything is committed, pushed, and documented. The system is stable and ready for Phase 3 development.

**Next session can start with:**
1. Review this document
2. Choose Phase 3 feature to implement
3. Continue building!
