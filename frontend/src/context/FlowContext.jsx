import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

const FlowContext = createContext(null)

const STORAGE_KEY = 'healthguard-flow'

const EMPTY_STATE = {
  sessionId: null,
  profileId: null,
  questions: [],
  reportInfo: null,
  lastAnalysisId: null,
  profileDraft: null,
  symptomDraft: null,
  followUpAnswers: {},
}

function loadInitial() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (raw) return { ...EMPTY_STATE, ...JSON.parse(raw) }
  } catch {
    /* ignore corrupted state */
  }
  return { ...EMPTY_STATE }
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
    setFlow((prev) => ({
      ...EMPTY_STATE,
      sessionId,
      profileId,
      profileDraft: prev.profileDraft,
    }))
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

  const setProfileDraft = useCallback((profileDraft) => {
    setFlow((prev) => ({ ...prev, profileDraft }))
  }, [])

  const setSymptomDraft = useCallback((symptomDraft) => {
    setFlow((prev) => ({ ...prev, symptomDraft }))
  }, [])

  const setFollowUpAnswers = useCallback((followUpAnswers) => {
    setFlow((prev) => ({ ...prev, followUpAnswers }))
  }, [])

  const reset = useCallback(() => {
    setFlow({ ...EMPTY_STATE })
  }, [])

  const value = useMemo(
    () => ({
      ...flow,
      startSession,
      setQuestions,
      setReportInfo,
      setLastAnalysisId,
      setProfileDraft,
      setSymptomDraft,
      setFollowUpAnswers,
      reset,
    }),
    [flow, startSession, setQuestions, setReportInfo, setLastAnalysisId, setProfileDraft, setSymptomDraft, setFollowUpAnswers, reset],
  )

  return <FlowContext.Provider value={value}>{children}</FlowContext.Provider>
}

export function useFlow() {
  const ctx = useContext(FlowContext)
  if (!ctx) throw new Error('useFlow must be used inside FlowProvider')
  return ctx
}
