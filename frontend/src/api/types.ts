export type RetrievalMode = 'inference_network' | 'vector'

export interface SearchResultItem {
  doc_id: string
  title: string
  url: string
  source: string
  score: number
  relevance: number
  snippet: string
}

export interface SearchResponse {
  query: string
  expanded_query: string | null
  mode: RetrievalMode
  used_web_fallback: boolean
  results: SearchResultItem[]
}

export interface Citation {
  index: number
  doc_id: string
  title: string
  url: string
  source: string
}

export interface RagSource {
  doc_id: string
  title: string
  url: string
  source: string
}

export interface RagAnswerResponse {
  query: string
  answer: string
  citations: Citation[]
  sources: RagSource[]
  used_web_fallback: boolean
}

export interface RecommendationItem {
  doc_id: string
  title: string
  url: string
  source: string
  score: number
}

export interface RecommendationResponse {
  user_id: string
  results: RecommendationItem[]
}

export interface ImageResultItem {
  doc_id: string
  title: string
  url: string
  image_url: string
  similarity: number
}

export interface ImageSearchResponse {
  query: string
  results: ImageResultItem[]
}

export interface FeedbackResponse {
  id: number
  query: string
  doc_id: string
  vote: 1 | -1
  user_id: string
}
