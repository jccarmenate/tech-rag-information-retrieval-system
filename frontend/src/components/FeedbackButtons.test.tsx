import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import * as apiClient from '../api/client'
import { FeedbackButtons } from './FeedbackButtons'

describe('FeedbackButtons', () => {
  it('submits an upvote and calls onVoted', async () => {
    const submitSpy = vi
      .spyOn(apiClient, 'submitFeedback')
      .mockResolvedValue({ id: 1, query: 'q', doc_id: 'doc-1', vote: 1, user_id: 'u1' })
    const onVoted = vi.fn()

    render(<FeedbackButtons query="q" docId="doc-1" userId="u1" onVoted={onVoted} />)
    fireEvent.click(screen.getByTitle('Relevant'))

    await waitFor(() => expect(onVoted).toHaveBeenCalled())
    expect(submitSpy).toHaveBeenCalledWith('q', 'doc-1', 1, 'u1')
  })

  it('does not call onVoted for a downvote', async () => {
    vi.spyOn(apiClient, 'submitFeedback').mockResolvedValue({
      id: 2,
      query: 'q',
      doc_id: 'doc-1',
      vote: -1,
      user_id: 'u1',
    })
    const onVoted = vi.fn()

    render(<FeedbackButtons query="q" docId="doc-1" userId="u1" onVoted={onVoted} />)
    fireEvent.click(screen.getByTitle('Not relevant'))

    await waitFor(() => expect(screen.getByTitle('Not relevant')).not.toBeDisabled())
    expect(onVoted).not.toHaveBeenCalled()
  })
})
