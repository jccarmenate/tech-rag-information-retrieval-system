import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { Filters } from './Filters'

describe('Filters', () => {
  it('calls onModeChange when a different retrieval model is selected', () => {
    const onModeChange = vi.fn()
    render(
      <Filters
        mode="inference_network"
        onModeChange={onModeChange}
        expand={false}
        onExpandChange={vi.fn()}
      />,
    )

    fireEvent.change(screen.getByLabelText('Retrieval model'), { target: { value: 'vector' } })

    expect(onModeChange).toHaveBeenCalledWith('vector')
  })

  it('calls onExpandChange when the expand checkbox is toggled', () => {
    const onExpandChange = vi.fn()
    render(
      <Filters
        mode="inference_network"
        onModeChange={vi.fn()}
        expand={false}
        onExpandChange={onExpandChange}
      />,
    )

    fireEvent.click(screen.getByRole('checkbox'))

    expect(onExpandChange).toHaveBeenCalledWith(true)
  })
})
