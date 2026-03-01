export interface CaseData {
  id: number
  case_name: string
  court: string
  date_decided: string | null
  citation: string | null
  summary: string | null
  pdf_url: string | null
  saflii_url: string
}

export interface SearchParams {
  q?: string
  court?: string
  year_from?: string
  year_to?: string
  judge?: string
  party?: string
  page?: string
  source?: string
}

export interface SearchResponse {
  results: CaseData[]
  total: number
  page: number
}

export interface SearchSource {
  id: string
  label: string
  search(params: SearchParams): Promise<SearchResponse>
}
