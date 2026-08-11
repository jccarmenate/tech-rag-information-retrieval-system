import type {
  FeedbackResponse,
  ImageSearchResponse,
  RagAnswerResponse,
  RecommendationResponse,
  RetrievalMode,
  SearchResponse,
} from './types'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!response.ok) {
    throw new Error(`Request to ${path} failed with status ${response.status}`)
  }
  return response.json() as Promise<T>
}

export interface SearchParams {
  q: string
  topK?: number
  mode?: RetrievalMode
  expand?: boolean
}

export function search({ q, topK = 10, mode = 'inference_network', expand = false }: SearchParams) {
  const params = new URLSearchParams({
    q,
    top_k: String(topK),
    mode,
    expand: String(expand),
  })
  return request<SearchResponse>(`/api/search?${params}`)
}

export function askRag(q: string, topK = 5) {
  const params = new URLSearchParams({ q, top_k: String(topK) })
  return request<RagAnswerResponse>(`/api/rag/answer?${params}`)
}

export function searchImages(q: string, topK = 8) {
  const params = new URLSearchParams({ q, top_k: String(topK) })
  return request<ImageSearchResponse>(`/api/multimodal/search?${params}`)
}

export function getRecommendations(userId: string, topK = 8) {
  const params = new URLSearchParams({ user_id: userId, top_k: String(topK) })
  return request<RecommendationResponse>(`/api/recommendations?${params}`)
}

export function submitFeedback(query: string, docId: string, vote: 1 | -1, userId: string) {
  return request<FeedbackResponse>('/api/feedback', {
    method: 'POST',
    body: JSON.stringify({ query, doc_id: docId, vote, user_id: userId }),
  })
}
