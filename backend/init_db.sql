-- Document Library Database Schema
-- This file contains the complete database schema
-- IMPORTANT: Keep this file synchronized with any model changes in backend/app/models/

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);

-- Tags table
CREATE TABLE IF NOT EXISTS tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    color VARCHAR(7),
    category VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_tags_name ON tags(name);

-- Documents table (without foreign key to document_versions initially)
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    original_filename VARCHAR(500) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_size BIGINT NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    storage_path VARCHAR(1000) NOT NULL,
    uploaded_by UUID NOT NULL REFERENCES users(id),
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    current_version_id UUID,
    processing_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    processing_progress INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_documents_title ON documents(title);
CREATE INDEX IF NOT EXISTS ix_documents_file_hash ON documents(file_hash);
CREATE INDEX IF NOT EXISTS ix_documents_uploaded_at ON documents(uploaded_at);

-- Document versions table
CREATE TABLE IF NOT EXISTS document_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    storage_path VARCHAR(1000) NOT NULL,
    file_size BIGINT NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    change_summary TEXT,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_document_versions_document_id ON document_versions(document_id);
CREATE INDEX IF NOT EXISTS ix_document_versions_created_at ON document_versions(created_at);

-- Add foreign key constraint from documents to document_versions
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_documents_current_version'
    ) THEN
        ALTER TABLE documents ADD CONSTRAINT fk_documents_current_version
        FOREIGN KEY (current_version_id) REFERENCES document_versions(id);
    END IF;
END $$;

-- Document text table
CREATE TABLE IF NOT EXISTS document_text (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    version_id UUID NOT NULL REFERENCES document_versions(id) ON DELETE CASCADE,
    extracted_text TEXT,
    ocr_applied BOOLEAN NOT NULL DEFAULT false,
    extraction_method VARCHAR(100),
    extracted_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_document_text_document_id ON document_text(document_id);

-- Document metadata table
CREATE TABLE IF NOT EXISTS document_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    version_id UUID NOT NULL REFERENCES document_versions(id) ON DELETE CASCADE,
    author VARCHAR(255),
    created_date TIMESTAMP,
    modified_date TIMESTAMP,
    language VARCHAR(10),
    page_count INTEGER,
    word_count INTEGER,
    auto_tags TEXT[],
    categories TEXT[],
    summary TEXT,
    entities JSONB,
    metadata_json JSONB,
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ai_model_used VARCHAR(100)
);
CREATE INDEX IF NOT EXISTS ix_document_metadata_document_id ON document_metadata(document_id);

-- Document embeddings table
CREATE TABLE IF NOT EXISTS document_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    version_id UUID NOT NULL REFERENCES document_versions(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    model_used VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
    -- Note: embedding_vector column will be added after pgvector extension is enabled
    -- embedding_vector vector(1536)
);
CREATE INDEX IF NOT EXISTS ix_document_embeddings_document_id ON document_embeddings(document_id);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    session_id UUID,
    details JSONB,
    result VARCHAR(20) NOT NULL,
    error_message TEXT
);
CREATE INDEX IF NOT EXISTS ix_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS ix_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS ix_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX IF NOT EXISTS ix_audit_logs_resource_id ON audit_logs(resource_id);
CREATE INDEX IF NOT EXISTS ix_audit_logs_timestamp ON audit_logs(timestamp);

-- Create default admin user (password: admin)
INSERT INTO users (id, email, hashed_password, full_name, role, is_active, created_at, updated_at)
SELECT
    uuid_generate_v4(),
    'admin@admin.com',
    '$2b$12$WI3w13pW3Bzuh95hIvAqoudFw9K5vGPh8yOF5u35ElhIXygkMB3mq',
    'Administrator',
    'admin',
    true,
    NOW(),
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'admin@admin.com');
