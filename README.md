# Document Library System

A comprehensive, fully containerized document management system with AI-powered classification, full-text search, version control, and audit trails.

## Features

- **Smart Document Classification** - AI-powered auto-tagging and categorization using Claude
- **Full-Text Search** - Search document titles AND contents (PDFs, Word docs, images)
- **OCR Support** - Extract text from scanned documents and images
- **Version Control** - Track all document versions with visual/text diffs
- **Audit Trail** - Complete logging of all user actions
- **Metadata Extraction** - Automatic metadata generation and search
- **Background Processing** - Async processing with real-time progress updates
- **Fully Containerized** - All services run in Docker containers
- **Horizontally Scalable** - Scale frontend, backend, and workers independently

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│               NGINX Reverse Proxy (Port 80)              │
│         Routes: / → Frontend, /api → Backend             │
└────────────┬─────────────────────────────┬──────────────┘
             │                             │
    ┌────────▼────────┐          ┌────────▼────────┐
    │   Frontend      │          │    Backend      │
    │   Container     │          │   Container     │
    │  (React+Vite)   │          │   (FastAPI)     │
    │                 │          │                 │
    │  Scalable ×N    │          │  Scalable ×N    │
    └─────────────────┘          └────────┬────────┘
                                          │
                                 ┌────────▼────────┐
                                 │  Celery Worker  │
                                 │   Container(s)  │
                                 │  Scalable ×N    │
                                 └────────┬────────┘
                                          │
         ┌────────────────────────────────┼────────────────┐
         │                                │                │
    ┌────▼──────┐  ┌──────────┐  ┌───────▼────┐  ┌───────▼─────┐
    │PostgreSQL │  │  MinIO   │  │   Redis    │  │ Meilisearch │
    └───────────┘  └──────────┘  └────────────┘  └─────────────┘
```

## Technology Stack

### Frontend
- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **Styling:** TailwindCSS
- **Container:** nginx (production), Vite dev server (development)

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **ASGI Server:** Uvicorn (dev), Gunicorn (production)
- **Database:** PostgreSQL 16+ (metadata, users, audit)
- **Storage:** MinIO (S3-compatible object storage)
- **Search:** Meilisearch (full-text search)
- **Vector DB:** pgvector (semantic search)
- **Queue:** Celery + Redis (background jobs)
- **AI:** Claude 3.5 Sonnet (metadata generation)
- **OCR:** Tesseract + AWS Textract

### Infrastructure
- **Containerization:** Docker + Docker Compose
- **Reverse Proxy:** nginx
- **Orchestration:** Docker Compose (dev), Kubernetes-ready

## Quick Start

### Prerequisites

- Docker 24.0+
- Docker Compose 2.20+
- Git

**Note:** You do NOT need Python, Node.js, or any other dependencies installed on your host machine. Everything runs in containers!

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd document-library
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your settings (optional for development)
   ```

3. **Start the entire stack**
   ```bash
   docker-compose up -d
   ```

   This single command:
   - Builds all Docker images
   - Starts all containers in correct order
   - Sets up all networks and volumes
   - Waits for health checks

4. **Access the application**
   - **Application:** http://localhost:8080
   - **API Docs:** http://localhost:8080/docs
   - **MinIO Console:** http://localhost:9001
   - **Meilisearch:** http://localhost:7700
   - **Backend API (direct):** http://localhost:8800
   - **Frontend (direct):** http://localhost:8173

5. **View logs**
   ```bash
   # All services
   docker-compose logs -f

   # Specific service
   docker-compose logs -f backend
   docker-compose logs -f frontend
   docker-compose logs -f celery-worker
   ```

### Initial Setup

1. **Run database migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

2. **Create first user** (visit http://localhost and register)

That's it! No Python virtualenvs, no npm install, no local dependencies.

## Development

### Hot Reload

Both frontend and backend support hot reload in development mode:
- **Frontend:** Edit files in `frontend/src/` and see changes instantly
- **Backend:** Edit files in `backend/app/` and server auto-reloads

### Scaling Services

Scale any service independently:

```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3

# Scale celery workers to 5 instances
docker-compose up -d --scale celery-worker=5

# Scale frontend to 2 instances
docker-compose up -d --scale frontend=2
```

### Rebuild After Changes

```bash
# Rebuild all containers
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build backend
```

### Execute Commands in Containers

```bash
# Run backend shell
docker-compose exec backend bash

# Run database migrations
docker-compose exec backend alembic upgrade head

# Access Python shell
docker-compose exec backend python

# Access PostgreSQL
docker-compose exec postgres psql -U doclib -d document_library

# Frontend shell
docker-compose exec frontend sh
```

## Production Deployment

Use the production compose file for optimized builds:

```bash
# Start with production settings
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale for production load
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d \
  --scale backend=5 \
  --scale celery-worker=10 \
  --scale frontend=3
```

Production features:
- Multi-stage builds (smaller images)
- No source code volumes (faster, isolated)
- Resource limits and reservations
- Optimized configurations
- Security hardening

## Project Structure

```
document-library/
├── docker-compose.yml              # Base configuration
├── docker-compose.override.yml     # Development overrides (auto-loaded)
├── docker-compose.prod.yml         # Production overrides
├── .env.example                    # Environment template
├── .env                            # Your environment (create from example)
│
├── nginx/
│   ├── Dockerfile                  # Reverse proxy image
│   └── nginx.conf                  # Proxy configuration
│
├── backend/
│   ├── Dockerfile                  # Multi-stage Python build
│   ├── app/
│   │   ├── main.py                 # FastAPI application
│   │   ├── api/                    # API endpoints
│   │   ├── models/                 # Database models
│   │   ├── schemas/                # Pydantic schemas
│   │   ├── services/               # Business logic
│   │   └── core/                   # Config, security
│   ├── alembic/                    # Database migrations
│   └── requirements.txt            # Python dependencies
│
└── frontend/
    ├── Dockerfile                  # Multi-stage React build
    ├── nginx.conf                  # Production server config
    ├── src/
    │   ├── pages/                  # React pages
    │   ├── components/             # Reusable components
    │   ├── services/               # API client
    │   ├── contexts/               # React contexts
    │   └── types/                  # TypeScript types
    └── package.json                # Node dependencies
```

## Container Details

### Services

| Service | Container Name | Port(s) | Purpose |
|---------|---------------|---------|---------|
| nginx | doclib-nginx | 8080 | Reverse proxy (main entry) |
| frontend | doclib-frontend | 8173 | React application |
| backend | doclib-backend | 8800 | FastAPI server |
| celery-worker | doclib-celery-worker | - | Background jobs |
| postgres | doclib-postgres | 5433 | Database |
| minio | doclib-minio | 9000, 9001 | Object storage |
| redis | doclib-redis | 6380 | Cache & queue |
| meilisearch | doclib-meilisearch | 7700 | Search engine |

### Health Checks

All services have health checks:
- Containers won't be marked healthy until ready
- Dependent services wait for dependencies
- nginx starts only after frontend and backend are healthy

### Volumes

Persistent data volumes:
- `doclib_postgres_data` - Database data
- `doclib_minio_data` - Document storage
- `doclib_redis_data` - Redis persistence
- `doclib_meilisearch_data` - Search indexes

## Common Tasks

### Stop All Services
```bash
docker-compose down
```

### Stop and Remove Volumes (CAUTION: deletes all data)
```bash
docker-compose down -v
```

### View Container Status
```bash
docker-compose ps
```

### Monitor Resource Usage
```bash
docker stats
```

### Clean Up Everything
```bash
# Stop containers
docker-compose down

# Remove images
docker-compose down --rmi all

# Remove volumes (data loss!)
docker-compose down -v
```

## Development Workflow

1. **Make changes** to source code (auto-mounted via volumes)
2. **See changes** immediately (hot reload)
3. **Test** with `docker-compose exec backend pytest`
4. **Commit** when ready

No need to rebuild containers for code changes!

## Environment Variables

Key variables in `.env`:

```bash
# Security
SECRET_KEY=generate-a-secure-random-key-here

# Database
POSTGRES_PASSWORD=change-in-production

# MinIO
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key

# AI (optional)
ANTHROPIC_API_KEY=your-claude-api-key
OPENAI_API_KEY=your-openai-key
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs <service-name>

# Check health status
docker-compose ps
```

### Database connection errors
```bash
# Ensure PostgreSQL is healthy
docker-compose ps postgres

# Check connection from backend
docker-compose exec backend python -c "from app.db.base import engine; print(engine)"
```

### Port already in use
```bash
# Change port in docker-compose.yml or stop conflicting service
sudo lsof -i :8080
```

Note: Ports chosen to avoid browser-blocked "unsafe ports" and common conflicts.

### Reset everything
```bash
docker-compose down -v
docker-compose up -d --build
docker-compose exec backend alembic upgrade head
```

## API Documentation

Once running, visit http://localhost:8080/docs for interactive API documentation (Swagger UI).

## Roadmap

### Phase 1: Core Infrastructure ✅ COMPLETE
- [x] Fully containerized architecture
- [x] Backend API with authentication
- [x] Frontend with login/register
- [x] Database models
- [x] Docker Compose setup

### Phase 2: Document Processing (Current)
- [ ] File upload to MinIO
- [ ] Text extraction (Apache Tika)
- [ ] OCR integration (Tesseract)
- [ ] Background job processing

### Phase 3: Search & AI
- [ ] Meilisearch integration
- [ ] Claude AI metadata generation
- [ ] Semantic search (pgvector)
- [ ] Advanced search UI

### Phase 4: Version Control & Audit
- [ ] Document versioning
- [ ] Diff implementation
- [ ] Comprehensive audit logging
- [ ] Version history UI

### Phase 5: Production Ready
- [ ] Performance optimization
- [ ] Admin dashboard
- [ ] Monitoring (Prometheus/Grafana)
- [ ] CI/CD pipeline

## Contributing

This is a personal project. Feel free to fork and adapt for your needs.

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.
