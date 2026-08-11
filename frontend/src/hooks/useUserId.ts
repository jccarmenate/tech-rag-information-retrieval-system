import { useState } from 'react'

const STORAGE_KEY = 'coderadar_user_id'

function createUserId(): string {
  return `guest-${Math.random().toString(36).slice(2, 10)}`
}

/** A stable, anonymous per-browser id so feedback and recommendations can be
 * scoped to "this visitor" without requiring accounts or login. */
export function useUserId(): string {
  const [userId] = useState(() => {
    const existing = localStorage.getItem(STORAGE_KEY)
    if (existing) return existing
    const created = createUserId()
    localStorage.setItem(STORAGE_KEY, created)
    return created
  })
  return userId
}
