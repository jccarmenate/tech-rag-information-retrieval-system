import type { SearchResultItem } from '../api/types'
import { ResultCard } from './ResultCard'
import './ResultsList.css'

interface ResultsListProps {
  results: SearchResultItem[]
  query: string
  userId: string
  usedWebFallback: boolean
}

export function ResultsList({ results, query, userId, usedWebFallback }: ResultsListProps) {
  if (results.length === 0) {
    return <p className="results-list__empty">No results yet. Try a search above.</p>
  }

  return (
    <div className="results-list">
      {usedWebFallback && (
        <p className="results-list__notice">
          🌐 The local corpus didn't have enough coverage for this query, so results were
          augmented with a live web search.
        </p>
      )}
      {results.map((result, index) => (
        <ResultCard
          key={result.doc_id}
          result={result}
          position={index + 1}
          query={query}
          userId={userId}
        />
      ))}
    </div>
  )
}
