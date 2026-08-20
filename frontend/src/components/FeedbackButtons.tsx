import { useState } from 'react'
import { submitFeedback } from '../api/client'
import './FeedbackButtons.css'

interface FeedbackButtonsProps {
  query: string
  docId: string
  userId: string
  onVoted?: () => void
}

export function FeedbackButtons({ query, docId, userId, onVoted }: FeedbackButtonsProps) {
  const [vote, setVote] = useState<1 | -1 | null>(null)
  const [pending, setPending] = useState(false)

  async function handleVote(nextVote: 1 | -1) {
    if (pending || vote === nextVote) return
    setPending(true)
    try {
      await submitFeedback(query, docId, nextVote, userId)
      setVote(nextVote)
      if (nextVote === 1) onVoted?.()
    } catch {
      // feedback is a nice-to-have signal; a failed request shouldn't
      // interrupt the user's search session
    } finally {
      setPending(false)
    }
  }

  return (
    <div className="feedback-buttons" role="group" aria-label="Was this result relevant?">
      <button
        type="button"
        className={`feedback-buttons__btn ${vote === 1 ? 'feedback-buttons__btn--active-up' : ''}`}
        onClick={() => handleVote(1)}
        disabled={pending}
        title="Relevant"
      >
        👍
      </button>
      <button
        type="button"
        className={`feedback-buttons__btn ${vote === -1 ? 'feedback-buttons__btn--active-down' : ''}`}
        onClick={() => handleVote(-1)}
        disabled={pending}
        title="Not relevant"
      >
        👎
      </button>
    </div>
  )
}
