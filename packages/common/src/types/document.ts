export type DocumentStatus = 'processing' | 'ready' | 'failed'

export interface Clause {
  id: string
  text: string
  section: string | null
  page: number | null
}

export interface Document {
  id: string
  matter_id: string
  name: string
  status: DocumentStatus
  uploaded_at: string
  clauses: Clause[]
}

export interface ProvisionMapping {
  clause_id: string
  clause_text: string
  case_id: number
  case_name: string
  relevance: 'supports' | 'contradicts' | 'neutral'
  explanation: string
  confidence: 'high' | 'medium' | 'low'
}

export interface AnalysisResult {
  document_id: string
  briefcase_id: string
  mappings: ProvisionMapping[]
  flags: string[]
  citations: string[]
  created_at: string
}
