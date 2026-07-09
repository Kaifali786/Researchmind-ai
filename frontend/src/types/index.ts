export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  avatar_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  full_name: string;
  username: string;
  email: string;
  password: string;
}

export interface Document {
  id: string;
  title: string;
  filename: string;
  file_type: 'pdf' | 'docx' | 'txt' | 'md' | 'epub';
  file_size: number;
  page_count: number;
  upload_date: string;
  status: 'processing' | 'ready' | 'error';
  summary?: string;
  tags: string[];
  user_id: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  document_ids?: string[];
  citations?: Citation[];
}

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  document_ids: string[];
  created_at: string;
  updated_at: string;
}

export interface Citation {
  id: string;
  text: string;
  source: string;
  authors: string[];
  year: number;
  page?: number;
  doi?: string;
  url?: string;
  format: 'apa' | 'mla' | 'chicago' | 'harvard' | 'ieee';
}

export interface Note {
  id: string;
  title: string;
  content: string;
  document_id?: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface AnalyticsData {
  total_papers: number;
  questions_asked: number;
  notes_saved: number;
  active_sessions: number;
  reading_progress: ReadingProgress[];
  recent_activity: ActivityItem[];
}

export interface ReadingProgress {
  date: string;
  papers_read: number;
  questions: number;
}

export interface ActivityItem {
  id: string;
  type: 'upload' | 'chat' | 'note' | 'citation';
  description: string;
  timestamp: string;
  document_title?: string;
}

export interface CompareResult {
  id: string;
  document_ids: string[];
  similarities: string[];
  differences: string[];
  summary: string;
  created_at: string;
}

export interface KnowledgeNode {
  id: string;
  label: string;
  type: 'concept' | 'paper' | 'author' | 'topic';
  connections: string[];
}

export interface KnowledgeGraph {
  nodes: KnowledgeNode[];
  edges: Array<{ source: string; target: string; label: string }>;
}

export type NavItem = {
  label: string;
  href: string;
  icon: string;
  badge?: number;
};
