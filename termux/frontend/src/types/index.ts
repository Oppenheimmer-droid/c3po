// User and Auth Types
export type UserRole = 'superadmin' | 'academy_admin' | 'teacher' | 'student' | 'parent'

export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  role: UserRole
  tenant_id: string
  tenant_name?: string
  is_active: boolean
  is_verified: boolean
  last_login?: string
  created_at: string
}

export interface Tenant {
  id: string
  name: string
  slug: string
  status: 'active' | 'suspended' | 'pending'
  created_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface LoginCredentials {
  email: string
  password: string
}

// Document Types
export interface Document {
  id: string
  tenant_id: string
  title: string
  original_filename: string
  file_size: number
  mime_type: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  page_count?: number
  chunk_count?: number
  subject_id?: string
  topic_id?: string
  difficulty?: number
  created_at: string
}

export interface DocumentChunk {
  id: string
  content: string
  chunk_index: number
  page_number?: number
}

// Chat Types
export interface ChatSession {
  id: string
  tenant_id: string
  user_id: string
  title: string
  document_id?: string
  subject_id?: string
  message_count: number
  is_archived: boolean
  last_message_at?: string
  created_at: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  input_tokens: number
  output_tokens: number
  created_at: string
}

export interface Citation {
  chunk_id: string
  source: string
  page?: number
  text?: string
}

// Evaluation Types
export interface Evaluation {
  id: string
  tenant_id: string
  document_id: string
  title: string
  description?: string
  evaluation_type: 'quiz' | 'exam' | 'practice'
  question_count: number
  time_limit_minutes?: number
  passing_score: number
  difficulty: number
  is_published: boolean
  total_attempts: number
  avg_score?: number
  created_at: string
}

export interface Question {
  id: string
  question_text: string
  question_type: 'multiple_choice' | 'true_false' | 'short_answer'
  difficulty: number
  points: number
  order_index: number
  options?: string[]
}

export interface EvaluationAttempt {
  id: string
  evaluation_id: string
  started_at: string
  completed_at?: string
  score?: number
  passed?: boolean
  time_spent_seconds?: number
}

// Analytics Types
export interface TenantAnalytics {
  total_users: number
  active_users: number
  total_documents: number
  total_chat_sessions: number
  total_evaluations: number
  total_tokens_used: number
  avg_evaluation_score?: number
}

export interface StudentProgress {
  total_attempts: number
  completed_attempts: number
  avg_score: number
  best_score: number
  pass_rate: number
  weak_topics: string[]
  strong_topics: string[]
}

// Subject Types
export interface Subject {
  id: string
  name: string
  code: string
  description?: string
}

export interface Topic {
  id: string
  name: string
  description?: string
  difficulty: number
}

// API Response Types
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface ApiError {
  detail: string
  code?: string
}

// Settings Types
export interface UserSettings {
  theme: 'light' | 'dark' | 'system'
  ai_provider: 'openai' | 'ollama'
  ollama_endpoint?: string
  notifications_enabled: boolean
}