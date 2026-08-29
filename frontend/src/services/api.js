const BASE = import.meta.env.VITE_API_BASE_URL ?? '/api'

export class ApiError extends Error {
  constructor(message, status, code, details) {
    super(message)
    this.status = status
    this.code = code
    this.details = details
  }
}

async function request(path, { method = 'GET', body, formData } = {}) {
  let response
  try {
    response = await fetch(`${BASE}${path}`, {
      method,
      headers: formData ? undefined : { 'Content-Type': 'application/json' },
      body: formData ?? (body ? JSON.stringify(body) : undefined),
    })
  } catch {
    throw new ApiError('Could not reach the server. Is the backend running on port 8000?', 0, 'network_error')
  }

  if (response.status === 204) return null

  let payload = null
  try {
    payload = await response.json()
  } catch {
    payload = null
  }

  if (!response.ok) {
    const err = payload?.error ?? {}
    throw new ApiError(err.message ?? `Request failed (HTTP ${response.status})`, response.status, err.code ?? 'unknown_error', err.details)
  }
  return payload
}

export const api = {
  health: () => request('/health'),

  createProfile: (profile) => request('/profile', { method: 'POST', body: profile }),
  getProfile: (id) => request(`/profile/${id}`),

  submitSymptoms: (symptoms) => request('/symptoms', { method: 'POST', body: symptoms }),

  generateFollowUp: (sessionId) => request('/follow-up', { method: 'POST', body: { session_id: sessionId } }),
  submitFollowUpAnswers: (sessionId, answers) =>
    request('/follow-up/answers', { method: 'POST', body: { session_id: sessionId, answers } }),

  uploadReport: (sessionId, file) => {
    const formData = new FormData()
    formData.append('session_id', sessionId)
    formData.append('file', file)
    return request('/reports/upload', { method: 'POST', formData })
  },
  explainReport: (reportId) => request(`/reports/${reportId}/explain`, { method: 'POST' }),

  analyze: (sessionId) => request('/analyze', { method: 'POST', body: { session_id: sessionId } }),
  getAnalysis: (id) => request(`/analyses/${id}`),
  listAnalyses: () => request('/analyses'),
}
