import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { SearchBar } from './SearchBar'

describe('SearchBar', () => {
  it('calls onSearch with the trimmed query on submit', () => {
    const onSearch = vi.fn()
    render(<SearchBar onSearch={onSearch} loading={false} />)

    fireEvent.change(screen.getByLabelText('Search query'), {
      target: { value: '  python async  ' },
    })
    fireEvent.click(screen.getByRole('button', { name: /search/i }))

    expect(onSearch).toHaveBeenCalledWith('python async')
  })

  it('disables the submit button when the query is empty', () => {
    render(<SearchBar onSearch={vi.fn()} loading={false} />)
    expect(screen.getByRole('button', { name: /search/i })).toBeDisabled()
  })

  it('disables the submit button while loading even with a query', () => {
    render(<SearchBar onSearch={vi.fn()} loading={true} />)
    fireEvent.change(screen.getByLabelText('Search query'), { target: { value: 'rust' } })
    expect(screen.getByRole('button', { name: /searching/i })).toBeDisabled()
  })

  it('does not call onSearch for a whitespace-only query', () => {
    const onSearch = vi.fn()
    render(<SearchBar onSearch={onSearch} loading={false} />)

    fireEvent.change(screen.getByLabelText('Search query'), { target: { value: '   ' } })
    fireEvent.click(screen.getByRole('button', { name: /search/i }))

    expect(onSearch).not.toHaveBeenCalled()
  })
})
