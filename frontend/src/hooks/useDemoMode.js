import { useEffect, useState } from 'react'
import { api } from '../services/api.js'

export function useDemoMode() {
  const [demoMode, setDemoMode] = useState(true)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    let cancelled = false
    api
      .health()
      .then((data) => {
        if (!cancelled) setDemoMode(Boolean(data.demo_mode))
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setReady(true)
      })
    return () => {
      cancelled = true
    }
  }, [])

  return { demoMode, ready }
}
