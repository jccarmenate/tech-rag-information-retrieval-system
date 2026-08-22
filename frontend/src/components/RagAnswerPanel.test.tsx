import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import type { Citation } from '../api/types'
import { RagAnswerPanel } from './RagAnswerPanel'

const citations: Citation[] = [
  { index: 1, doc_id: 'a', title: 'Source A', url: 'https://a.example', source: 'github' },
  { index: 2, doc_id: 'b', title: 'Source B', url: 'https://b.example', source: 'devto' },
]

describe('RagAnswerPanel', () => {
  it('shows a loading message while generating', () => {
    render(<RagAnswerPanel answer="" citations={[]} loading={true} />)
    expect(screen.getByText(/generating a grounded answer/i)).toBeInTheDocument()
  })

  it('renders nothing when there is no answer and not loading', () => {
    const { container } = render(<RagAnswerPanel answer="" citations={[]} loading={false} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('renders citation markers as links to their source', () => {
    render(
      <RagAnswerPanel
        answer="Python is popular for ML [1] while Rust favors safety [2]."
        citations={citations}
        loading={false}
      />,
    )

    const linkOne = screen.getByRole('link', { name: '[1]' })
    expect(linkOne).toHaveAttribute('href', 'https://a.example')
    const linkTwo = screen.getByRole('link', { name: '[2]' })
    expect(linkTwo).toHaveAttribute('href', 'https://b.example')
  })

  it('lists all cited sources below the answer', () => {
    render(<RagAnswerPanel answer="See [1] and [2]." citations={citations} loading={false} />)
    expect(screen.getByRole('link', { name: 'Source A' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Source B' })).toBeInTheDocument()
  })
})
