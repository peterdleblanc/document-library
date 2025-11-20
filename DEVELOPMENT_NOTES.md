# Development Notes & Context

This document contains important context and lessons learned during development.

## Session History

### Session 1: Initial Setup (2025-11-19)
- Created fully containerized architecture
- Set up Docker Compose with all services
- Implemented authentication (JWT)
- Built basic frontend (React + TypeScript)

### Session 2: Document Upload & Phase 2 (2025-11-19)
- Implemented MinIO file storage
- Created document upload/download APIs
- **Removed Podman, switched to Docker only**
- Built text extraction with Apache Tika
- Integrated Tesseract OCR
- Created background processing pipeline
- Set up database schema management system
- Fixed multiple bugs (bcrypt, API URLs, nginx)

## Important Context for Future Development

### Docker Setup

**Critical:** This system uses Docker, NOT Podman. Podman was removed because it was causing socket conflicts.

All Docker commands require `sudo`:
```bash
sudo docker compose ps
sudo docker compose logs -f
sudo docker compose up -d --build
```

The user is in the docker group but needs to log out/in for it to take effect without sudo.

### Database Schema Management

**CRITICAL RULE:** Whenever you modify database models, you MUST update `backend/init_db.sql`.

A git pre-commit hook enforces this:
- Located at: `.git-hooks/pre-commit`
- Warns if models changed without updating SQL
- Warns if SQL changed without updating models

To update schema:
1. Edit `backend/app/models/*.py`
2. Update `backend/init_db.sql`
3. Run `./backend/reset_db.sh` to test
4. Commit both files together

### Circular Foreign Key Dependencies

The schema has a circular dependency between `documents` and `document_versions`:
- `documents.current_version_id` → `document_versions.id`
- `document_versions.document_id` → `documents.id`

This is handled in `init_db.sql` by:
1. Creating `documents` WITHOUT the FK constraint
2. Creating `document_versions` WITH its FK
3. Adding the `documents.current_version_id` FK afterward (lines 66-74)

### Authentication

**Password Hashing:**
- Uses **direct bcrypt**, NOT passlib
- Passwords truncated to 72 bytes (bcrypt limit)
- Code location: `backend/app/core/security.py:11-27`

**Default Admin User:**
- Email: `admin@admin.com`
- Password: `admin`
- Created automatically by `init_db.sql` (line 145)
- **Change this in production!**

### Frontend API Configuration

**Critical:** The frontend API base URL is set to `/api` in `frontend/.env`:
```
VITE_API_URL=/api
```

All API endpoints in `frontend/src/services/api.ts` use `/v1/...` (not `/api/v1/...`).

Nginx routes:
- `/` → frontend:5173
- `/api` → backend:8000

**Do NOT add `/api` prefix to endpoints** - it's already in the base URL.

### Port Configuration

**External Ports (from docker-compose.yml):**
- 8080 - nginx (main entry point)
- 8173 - frontend (Vite dev server)
- 8800 - backend (FastAPI)
- 5433 - postgres
- 6379, 6380 - redis
- 9000, 9001 - minio
- 7700 - meilisearch

**Internal Container Ports:**
- frontend: 5173 (Vite)
- backend: 8000 (uvicorn)
- postgres: 5432
- redis: 6379
- minio: 9000 (API), 9001 (console)
- meilisearch: 7700

### Background Processing

**Celery Configuration:**
- Broker: Redis (`redis://redis:6379/0`)
- Backend: Redis (`redis://redis:6379/1`)
- Worker concurrency: 8 (solo pool)

**Tasks:**
- `process_document` - Main document processing pipeline
- `cleanup_temp_files` - Periodic cleanup (not yet implemented)

**Task Registration:**
- Auto-discovery in `backend/app/tasks/`
- Named explicitly: `@celery_app.task(name="process_document")`

### Text Extraction

**Apache Tika:**
- Version: 2.6.0 (NOT apache-tika)
- Supports: PDF, Word, Excel, PowerPoint, HTML, RTF, text
- Returns metadata along with text
- Location: `backend/app/services/text_extraction_service.py`

**Tesseract OCR:**
- Binary location: `/usr/bin/tesseract`
- Python wrapper: pytesseract==0.3.10
- Supports: Images (PNG, JPG) and scanned PDFs
- PDF processing: Uses pdf2image to convert pages → images → OCR
- Location: `backend/app/services/ocr_service.py`

**OCR Triggers:**
- All image files (image/*)
- PDFs with < 100 characters of text (likely scanned)

### Document Processing Pipeline

**Flow:**
1. Upload → MinIO storage path: `documents/{year}/{month}/{doc_id}/v{version}.ext`
2. Create DB records in `documents` and `document_versions`
3. Queue Celery task: `process_document.delay(document_id)`
4. Worker downloads file from MinIO
5. Extracts text with Tika
6. Applies OCR if needed
7. Stores in `document_text` table
8. Updates `processing_status` and `processing_progress`

**Progress Tracking:**
- 0% - Pending
- 10% - Downloading file
- 30% - Extracting text
- 50% - OCR (if needed)
- 65% - Embeddings (Phase 3)
- 80% - AI metadata (Phase 3)
- 90% - Search indexing (Phase 3)
- 95% - Thumbnails (future)
- 100% - Completed

## Common Issues & Solutions

### Issue: "Cannot connect to Docker daemon at podman.sock"
**Solution:** Unset DOCKER_HOST environment variable:
```bash
unset DOCKER_HOST
sudo docker compose ps
```

### Issue: "Permission denied while connecting to Docker socket"
**Solution:** Use sudo OR log out and back in after adding user to docker group:
```bash
sudo docker compose ps
# OR
sudo usermod -aG docker $USER
# then logout/login
```

### Issue: "relation 'documents' does not exist"
**Solution:** Reset the database:
```bash
./backend/reset_db.sh
```

### Issue: Frontend shows 502 Bad Gateway
**Solution:** Check if backend is healthy:
```bash
sudo docker compose ps backend
sudo docker compose logs backend
```

### Issue: Celery worker not processing tasks
**Solution:** Check worker logs and Redis connection:
```bash
sudo docker compose logs celery-worker
sudo docker compose ps redis
```

### Issue: Text extraction fails
**Solution:** Check Tika is installed and file is accessible:
```bash
sudo docker compose exec backend python -c "import tika; print(tika.__version__)"
sudo docker compose logs celery-worker | grep -i error
```

## Code Patterns & Conventions

### Async/Sync Boundaries

**Celery tasks are synchronous**, so we use this pattern:
```python
@celery_app.task(bind=True, name="process_document")
def process_document(self, document_id: str):
    return asyncio.run(_process_document_async(self, document_id))

async def _process_document_async(task, document_id: str):
    # Async implementation here
    async with async_session_maker() as db:
        # Database operations
```

### Database Sessions

**FastAPI endpoints:**
```python
async def endpoint(db: AsyncSession = Depends(get_async_db)):
    # Use db here
```

**Celery tasks:**
```python
async with async_session_maker() as db:
    # Use db here
    await db.commit()
```

### Service Pattern

Services are singletons created at module level:
```python
class TextExtractionService:
    def extract_text(self, ...):
        pass

# Singleton
text_extraction_service = TextExtractionService()
```

Import and use:
```python
from app.services.text_extraction_service import text_extraction_service

text = text_extraction_service.extract_text(data, filename, mime_type)
```

### Error Handling in Tasks

Always update document status on failure:
```python
try:
    # Processing logic
    document.processing_status = "completed"
except Exception as e:
    document.processing_status = "failed"
    document.processing_progress = 0
    await db.commit()
    return {"status": "error", "message": str(e)}
```

## Dependencies to Know

### Python (backend/requirements.txt)
- fastapi==0.109.0 - Web framework
- uvicorn==0.27.0 - ASGI server
- sqlalchemy==2.0.25 - ORM
- asyncpg==0.29.0 - Async Postgres driver
- celery==5.3.6 - Background tasks
- redis==5.0.1 - Cache & queue
- minio==7.2.3 - S3 client
- tika==2.6.0 - Text extraction
- pytesseract==0.3.10 - OCR
- Pillow==10.2.0 - Image processing
- pdf2image==1.17.0 - PDF conversion
- bcrypt==4.1.2 - Password hashing
- pyjwt==2.8.0 - JWT tokens

### TypeScript (frontend/package.json)
- react==18.2.0
- typescript==5.3.3
- vite==5.0.11
- axios==1.6.5
- tailwindcss==3.4.1
- react-router-dom==6.21.2

## File Structure Reference

```
document-library/
├── .git-hooks/
│   └── pre-commit              # Schema sync validation
├── backend/
│   ├── app/
│   │   ├── api/v1/             # API endpoints
│   │   ├── core/               # Config, security
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # Business logic
│   │   │   ├── minio_service.py
│   │   │   ├── document_service.py
│   │   │   ├── text_extraction_service.py  # NEW
│   │   │   └── ocr_service.py              # NEW
│   │   ├── tasks/              # Celery tasks
│   │   │   └── document_tasks.py
│   │   ├── celery_app.py       # Celery config
│   │   └── main.py             # FastAPI app
│   ├── init_db.sql             # Complete schema
│   ├── reset_db.sh             # DB reset script
│   ├── DATABASE_SCHEMA.md      # Schema docs
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API client
│   │   └── types/              # TypeScript types
│   ├── .env                    # VITE_API_URL=/api
│   └── package.json
├── nginx/
│   └── nginx.conf              # Reverse proxy config
├── docker-compose.yml          # Base config
├── docker-compose.override.yml # Dev overrides
├── setup-hooks.sh              # Git hooks installer
├── PROJECT_STATUS.md           # Current status
└── DEVELOPMENT_NOTES.md        # This file
```

## Testing Strategy

### Manual Testing Workflow
1. Start services: `sudo docker compose up -d`
2. Check health: `sudo docker compose ps`
3. Access app: http://localhost:8080
4. Login: admin@admin.com / admin
5. Upload document (PDF or image)
6. Watch logs: `sudo docker compose logs -f celery-worker`
7. Check database:
   ```sql
   SELECT id, title, processing_status, processing_progress FROM documents;
   SELECT document_id, LENGTH(extracted_text), ocr_applied FROM document_text;
   ```

### What to Test
- [ ] User registration and login
- [ ] Document upload (PDF)
- [ ] Document upload (image - triggers OCR)
- [ ] Document upload (Word doc)
- [ ] Text extraction visible in logs
- [ ] Processing progress updates
- [ ] Document download
- [ ] Document delete

## Future Considerations

### Phase 3: Search & AI
- Need Anthropic API key for Claude
- Meilisearch already running but not integrated
- pgvector needs to be enabled in Postgres
- Consider chunking strategy for embeddings

### Phase 4: Version Control
- UI for version comparison
- Diff algorithm for documents
- Storage strategy for multiple versions

### Phase 5: Production
- Switch to production Docker target
- Add proper monitoring (Prometheus/Grafana)
- Implement rate limiting
- Add health check endpoints
- Set up CI/CD pipeline
- Security audit (especially file uploads)

## Environment Variables

Current `.env` settings (create from .env.example):
```bash
# Database
POSTGRES_DB=document_library
POSTGRES_USER=doclib
POSTGRES_PASSWORD=doclib_password_change_in_prod

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_BUCKET_NAME=documents

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Meilisearch
MEILI_MASTER_KEY=your_master_key_here

# Backend
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True

# Optional (Phase 3)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

## Remember for Tomorrow

1. **All docker commands need sudo** (or relogin to activate docker group)
2. **Schema changes require updating both models AND init_db.sql**
3. **Frontend API endpoints use /v1/... not /api/v1/...**
4. **Admin credentials: admin@admin.com / admin**
5. **Database reset: ./backend/reset_db.sh**
6. **Main app URL: http://localhost:8080**

## Quick Start for Next Session

```bash
# Navigate to project
cd /home/peter/claude/github-repos/document-library

# Check status
sudo docker compose ps

# View recent commits
git log --oneline -5

# Start if needed
sudo docker compose up -d

# Access app
firefox http://localhost:8080

# View logs
sudo docker compose logs -f celery-worker
```

Happy coding! 🚀
