#!/bin/bash
# Database Reset Script
# This script resets the database to a clean state and applies the schema

set -e

echo "🗄️  Resetting database schema..."

# Drop all tables (in correct order to handle foreign keys)
sudo docker compose exec postgres psql -U doclib -d document_library -c "
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS document_embeddings CASCADE;
DROP TABLE IF EXISTS document_metadata CASCADE;
DROP TABLE IF EXISTS document_text CASCADE;
DROP TABLE IF EXISTS document_versions CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS users CASCADE;
" 2>/dev/null || echo "Tables didn't exist, continuing..."

echo "✓ Dropped existing tables"

# Apply schema
echo "📝 Applying schema from init_db.sql..."
sudo docker compose exec -T postgres psql -U doclib -d document_library < backend/init_db.sql

echo "✅ Database schema initialized successfully!"
echo ""
echo "Default admin user created:"
echo "  Email: admin@admin.com"
echo "  Password: admin"
