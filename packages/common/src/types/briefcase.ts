export interface ReasonCase {
  id: string
  case_id: number
  content: string | null
  order: number
  created_at: string
  case_name: string | null
  court: string | null
  citation: string | null
  date_decided: string | null
}

export interface Reason {
  id: string
  title: string
  description: string | null
  content: string | null
  order: number
  created_at: string
  cases: ReasonCase[]
}

export interface Briefcase {
  id: string
  name: string
  description: string | null
  created_at: string
  updated_at: string
  reasons: Reason[]
}

export interface BriefcaseListResponse {
  briefcases: Briefcase[]
  total: number
}

export interface ContentVersion {
  id: string
  content: string
  version: number
  created_at: string
}

export interface GenerateResponse {
  content: string
}
