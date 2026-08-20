import type { SearchResultItem } from '../api/types'
import { FeedbackButtons } from './FeedbackButtons'
import './ResultCard.css'

interface ResultCardProps {
  result: SearchResultItem
  position: number
  query: string
  userId: string
  onVoted?: () => void
}

const SOURCE_LABELS: Record<string, string> = {
  github: 'GitHub',
  hackernews: 'Hacker News',
  devto: 'Dev.to',
  stackexchange: 'Stack Overflow',
  arxiv: 'arXiv',
  web: 'Web',
}

export function ResultCard({ result, position, query, userId, onVoted }: ResultCardProps) {
  const isTopResult = position <= 3

  return (
    <article className={`result-card ${isTopResult ? 'result-card--top' : ''}`}>
      <div className="result-card__position" aria-hidden="true">
        {position}
      </div>

      <div className="result-card__body">
        <div className="result-card__meta">
          <span className="result-card__source">
            {SOURCE_LABELS[result.source] ?? result.source}
          </span>
          <span className="result-card__score" title="Final positioning score">
            {(result.score * 100).toFixed(0)}% match
          </span>
        </div>

        <h3 className="result-card__title">
          <a href={result.url} target="_blank" rel="noreferrer">
            {result.title}
          </a>
        </h3>

        <p className="result-card__snippet">{result.snippet}</p>

        <div className="result-card__footer">
          <div className="result-card__score-bar" title={`Positioning score: ${result.score.toFixed(2)}`}>
            <div
              className="result-card__score-bar-fill"
              style={{ width: `${Math.min(result.score * 100, 100)}%` }}
            />
          </div>
          <FeedbackButtons
            query={query}
            docId={result.doc_id}
            userId={userId}
            onVoted={onVoted}
          />
        </div>
      </div>
    </article>
  )
}
