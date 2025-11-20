// User types
export interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Document types
export interface Document {
  id: string;
  title: string;
  original_filename: string;
  mime_type: string;
  file_size: number;
  file_hash: string;
  uploaded_by: string;
  uploaded_at: string;
  processing_status: string;
  processing_progress: number;
  metadata?: DocumentMetadata;
  current_version_id?: string;
}

export interface DocumentMetadata {
  author?: string;
  created_date?: string;
  modified_date?: string;
  language?: string;
  page_count?: number;
  word_count?: number;
  auto_tags: string[];
  categories: string[];
  summary?: string;
  entities?: Record<string, any>;
}

export interface DocumentListResponse {
  total: number;
  page: number;
  page_size: number;
  documents: Document[];
}

export interface DocumentUploadResponse {
  document_id: string;
  status: string;
  message: string;
}

// API Error types
export interface APIError {
  detail: string;
}
