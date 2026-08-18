import { useEffect, useState } from 'react'
import { getRecommendations } from '../api/client'
import type { RecommendationItem } from '../api/types'
import './RecommendationsPanel.css'

interface RecommendationsPanelProps {
  userId: string
  /** Bumped after every feedback vote so recommendations refresh once the
   * user has actually liked something (cold-start users get an empty panel). */
  refreshKey: number
}

export function RecommendationsPanel({ userId, refreshKey }: RecommendationsPanelProps) {
  const [items, setItems] = useState<RecommendationItem[]>([])

  useEffect(() => {
    let cancelled = false
    getRecommendations(userId)
      .then((res) => {
        if (!cancelled) setItems(res.results)
      })
      .catch(() => {
        if (!cancelled) setItems([])
      })
    return () => {
      cancelled = true
    }
  }, [userId, refreshKey])

  if (items.length === 0) {
    return (
      <aside className="recommendations">
        <h2 className="recommendations__heading">Recommended for you</h2>
        <p className="recommendations__empty">
          👍 a few results to get personalized recommendations here.
        </p>
      </aside>
    )
  }

  return (
    <aside className="recommendations">
      <h2 className="recommendations__heading">Recommended for you</h2>
      <ul className="recommendations__list">
        {items.map((item) => (
          <li key={item.doc_id} className="recommendations__item">
            <a href={item.url} target="_blank" rel="noreferrer">
              {item.title}
            </a>
            <span className="recommendations__source">{item.source}</span>
          </li>
        ))}
      </ul>
    </aside>
  )
}
