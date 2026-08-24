import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

const FlowContext = createContext(null)

const STORAGE_KEY = 'healthguard-flow'

function loadInitial() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch {
    /* ignore corrupted state */
  }
  return {
    sessionId: null,
    profileId: null,
    questions: [],
    reportInfo: null,
    lastAnalysisId: null,
  }
}

export function FlowProvider({ children }) {
  const [flow, setFlow] = useState(loadInitial)

  useEffect(() => {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(flow))
    } catch {
      /* storage unavailable */
    }
  }, [flow])

  const startSession = useCallback((profileId, sessionId) => {
    setFlow({ sessionId, profileId, questions: [], reportInfo: null, lastAnalysisId: null })
  }, [])

  const setQuestions = useCallback((questions) => {
    setFlow((prev) => ({ ...prev, questions }))
  }, [])

  const setReportInfo = useCallback((reportInfo) => {
    setFlow((prev) => ({ ...prev, reportInfo }))
  }, [])

  const setLastAnalysisId = useCallback((id) => {
    setFlow((prev) => ({ ...prev, lastAnalysisId: id }))
  }, [])

  const reset = useCallback(() => {
    setFlow({ sessionId: null, profileId: null, questions: [], reportInfo: null, lastAnalysisId: null })
  }, [])

  const value = useMemo(
    () => ({ ...flow, startSession, setQuestions, setReportInfo, setLastAnalysisId, reset }),
    [flow, startSession, setQuestions, setReportInfo, setLastAnalysisId, reset],
  )

  return <FlowContext.Provider value={value}>{children}</FlowContext.Provider>
}

export function useFlow() {
  const ctx = useContext(FlowContext)
  if (!ctx) throw new Error('useFlow must be used inside FlowProvider')
  return ctx
}
