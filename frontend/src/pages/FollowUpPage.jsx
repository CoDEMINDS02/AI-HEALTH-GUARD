import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Loader from '../components/Loader.jsx'
import Stepper from '../components/Stepper.jsx'
import { api } from '../services/api.js'
import { useFlow } from '../context/FlowContext.jsx'

export default function FollowUpPage() {
  const navigate = useNavigate()
  const { sessionId, questions, setQuestions } = useFlow()

  const [answers, setAnswers] = useState({})
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(questions.length === 0)

  useEffect(() => {
    if (!sessionId) {
      navigate('/profile')
      return
    }
    if (questions.length === 0) {
      api
        .generateFollowUp(sessionId)
        .then((data) => setQuestions(data.questions ?? []))
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false))
    }
  }, [sessionId, questions.length, navigate, setQuestions])

  const answeredCount = useMemo(
    () => questions.filter((q) => (answers[q] ?? '').trim()).length,
    [questions, answers],
  )
  const progress = questions.length > 0 ? Math.round((answeredCount / questions.length) * 100) : 0

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setBusy(true)
    try {
      const payload = questions.map((q) => ({ question: q, answer: answers[q] ?? '' }))
      await api.submitFollowUpAnswers(sessionId, payload)
      navigate('/report')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="fade-in">
      <Stepper current={2} />
      <div className="card">
        <h2>A few follow-up questions</h2>
        <p style={{ color: 'var(--text-2)' }}>
          These targeted questions help the assessment reflect what matters. You may skip any
          question.
        </p>

        {error && <div className="error-box" role="alert">{error}</div>}

        {loading && <Loader message="Preparing your questions…" />}

        {!loading && questions.length === 0 && !error && (
          <div className="empty-state">
            <div className="empty-icon" aria-hidden="true">💬</div>
            <h3>No questions needed</h3>
            <p>Your symptoms were detailed enough that no clarifying questions are required.</p>
            <button className="btn btn-primary" onClick={() => navigate('/report')}>
              Continue → Medical Report
            </button>
          </div>
        )}

        {!loading && questions.length > 0 && (
          <form onSubmit={handleSubmit}>
            <div
              className="followup-progress"
              role="progressbar"
              aria-valuemin={0}
              aria-valuemax={questions.length}
              aria-valuenow={answeredCount}
              aria-label={`${answeredCount} of ${questions.length} questions answered`}
            >
              <div className="followup-progress-bar" style={{ width: `${progress}%` }} />
            </div>

            <div className="q-card-list">
              {questions.map((q, i) => (
                <div className="q-card" key={q}>
                  <div className="q-index">Question {i + 1} of {questions.length}</div>
                  <div className="field q-item" style={{ marginBottom: 0 }}>
                    <label htmlFor={`q-${i}`} style={{ fontSize: 14.5 }}>{q}</label>
                    <input
                      id={`q-${i}`}
                      type="text"
                      value={answers[q] ?? ''}
                      onChange={(e) => setAnswers((prev) => ({ ...prev, [q]: e.target.value }))}
                      placeholder="Type your answer… (optional)"
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="btn-row">
              <button type="button" className="btn btn-secondary" onClick={() => navigate('/symptoms')}>
                ← Back
              </button>
              <button className="btn btn-primary" type="submit" disabled={busy}>
                {busy ? 'Saving…' : 'Continue → Medical Report'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
