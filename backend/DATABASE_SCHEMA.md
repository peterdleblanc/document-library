# Database Schema Management

## Overview

This document describes how to manage database schemas for the Document Library system.

## Important Files

- **`init_db.sql`** - The source of truth for the complete database schema
- **`reset_db.sh`** - Script to reset and reinitialize the database
- **`app/models/`** - SQLAlchemy model definitions (Python)

## Critical Rule: Schema Synchronization

⚠️ **WHENEVER you modify database models, you MUST update `init_db.sql`**

This ensures:
- New developers can initialize the database correctly
- Database can be reset to a known good state
- Schema documentation stays current
- CI/CD pipelines work correctly

## Schema Change Workflow

When changing the database schema:

1. **Modify the SQLAlchemy models** in `app/models/*.py`
2. **Update `init_db.sql`** with the corresponding SQL changes
3. **Test the changes** by running `./reset_db.sh`
4. **Verify the application works** with the new schema
5. **Commit both files together** in the same commit

### Example

```bash
# 1. Edit models
vim app/models/document.py

# 2. Update SQL schema
vim init_db.sql

# 3. Test by resetting database
./reset_db.sh

# 4. Test application
curl http://localhost:8080/api/v1/documents/

# 5. Commit both together
git add app/models/document.py init_db.sql
git commit -m "Add new field to document model"
```

## Database Operations

### Reset Database (Clean Slate)

```bash
# From project root
./backend/reset_db.sh
```

This will:
- Drop all existing tables
- Recreate tables from `init_db.sql`
- Create default admin user (admin@admin.com / admin)

### Apply Schema Manually

```bash
sudo docker compose exec -T postgres psql -U doclib -d document_library < backend/init_db.sql
```

### Connect to Database

```bash
# Interactive PostgreSQL shell
sudo docker compose exec postgres psql -U doclib -d document_library

# Run single query
sudo docker compose exec postgres psql -U doclib -d document_library -c "SELECT * FROM users;"
```

### Backup Database

```bash
# Create backup
sudo docker compose exec postgres pg_dump -U doclib document_library > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
sudo docker compose exec -T postgres psql -U doclib -d document_library < backup_20251120_123456.sql
```

## Schema Documentation

### Tables

1. **users** - User accounts and authentication
2. **documents** - Document metadata and references
3. **document_versions** - Version history for documents
4. **document_text** - Extracted text content
5. **document_metadata** - AI-generated and extracted metadata
6. **document_embeddings** - Vector embeddings for semantic search
7. **tags** - Categorization tags
8. **audit_logs** - Audit trail of all actions

### Circular Dependencies

The schema has a circular dependency between `documents` and `document_versions`:
- `documents.current_version_id` references `document_versions.id`
- `document_versions.document_id` references `documents.id`

This is handled in `init_db.sql` by:
1. Creating `documents` table without the foreign key constraint
2. Creating `document_versions` table with its foreign key
3. Adding the `documents.current_version_id` constraint afterward

## Migration Strategy (Future)

Currently using direct SQL schema management. For production:

### Option 1: Keep SQL-First Approach
- Pros: Simple, direct, no migration complexity
- Cons: Manual synchronization required
- Best for: Small teams, rapid development

### Option 2: Alembic Migrations
- Pros: Version-controlled schema changes
- Cons: More complex, migration files to maintain
- Best for: Production systems, large teams

To add Alembic later:
```bash
# Generate migration from models
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

## Troubleshooting

### Schema out of sync with models

If you get SQLAlchemy errors about missing tables/columns:

```bash
# Check what exists in database
sudo docker compose exec postgres psql -U doclib -d document_library -c "\dt"
sudo docker compose exec postgres psql -U doclib -d document_library -c "\d documents"

# Reset to clean state
./backend/reset_db.sh
```

### Alembic migration conflicts

If you have old Alembic migrations causing issues:

```bash
# Clear Alembic version table
sudo docker compose exec postgres psql -U doclib -d document_library -c "DROP TABLE IF EXISTS alembic_version;"

# Use SQL schema instead
./backend/reset_db.sh
```

### Foreign key violations

The schema is designed to handle foreign keys properly, but if you encounter issues:

```bash
# Check foreign key constraints
sudo docker compose exec postgres psql -U doclib -d document_library -c "
SELECT conname, conrelid::regclass, confrelid::regclass
FROM pg_constraint
WHERE contype = 'f';"
```

## Default Data

### Admin User

The schema automatically creates an admin user:
- **Email:** admin@admin.com
- **Password:** admin
- **Role:** admin

Change this password in production!

## Schema Maintenance Checklist

Before committing schema changes:

- [ ] Updated SQLAlchemy models in `app/models/`
- [ ] Updated `init_db.sql` with corresponding SQL
- [ ] Tested with `./reset_db.sh`
- [ ] Verified application works
- [ ] Updated this documentation if needed
- [ ] Both model and SQL files in same commit
