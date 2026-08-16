import type { Citation } from '../api/types'
import './RagAnswerPanel.css'

interface RagAnswerPanelProps {
  answer: string
  citations: Citation[]
  loading: boolean
}

const CITATION_RE = /\[(\d+)\]/g

function renderAnswerWithCitations(answer: string, citations: Citation[]) {
  const byIndex = new Map(citations.map((c) => [c.index, c]))
  const parts: (string | Citation)[] = []
  let lastEnd = 0

  for (const match of answer.matchAll(CITATION_RE)) {
    const index = Number(match[1])
    const citation = byIndex.get(index)
    if (!citation) continue
    parts.push(answer.slice(lastEnd, match.index))
    parts.push(citation)
    lastEnd = match.index! + match[0].length
  }
  parts.push(answer.slice(lastEnd))

  return parts.map((part, i) =>
    typeof part === 'string' ? (
      <span key={i}>{part}</span>
    ) : (
      <a
        key={i}
        className="rag-answer__citation"
        href={part.url}
        target="_blank"
        rel="noreferrer"
        title={part.title}
      >
        [{part.index}]
      </a>
    ),
  )
}

export function RagAnswerPanel({ answer, citations, loading }: RagAnswerPanelProps) {
  if (loading) {
    return (
      <section className="rag-answer rag-answer--loading">
        <p>Generating a grounded answer…</p>
      </section>
    )
  }

  if (!answer) return null

  return (
    <section className="rag-answer">
      <h2 className="rag-answer__heading">Answer</h2>
      <p className="rag-answer__text">{renderAnswerWithCitations(answer, citations)}</p>
      {citations.length > 0 && (
        <ul className="rag-answer__sources">
          {citations.map((c) => (
            <li key={c.index}>
              <span className="rag-answer__source-index">[{c.index}]</span>{' '}
              <a href={c.url} target="_blank" rel="noreferrer">
                {c.title}
              </a>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
