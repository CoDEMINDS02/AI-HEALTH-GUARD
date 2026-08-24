import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Stepper from '../components/Stepper.jsx'
import { api } from '../services/api.js'
import { useFlow } from '../context/FlowContext.jsx'

export default function FollowUpPage() {
  const navigate = useNavigate()
  const { sessionId, questions, setQuestions } = useFlow()

  const [answers, setAnswers] = useState({})
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

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
    }
  }, [sessionId, questions.length, navigate, setQuestions])

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
    <div>
      <Stepper current={2} />
      <div className="card">
        <h2>Follow-up questions</h2>
        <p style={{ color: 'var(--muted)' }}>
          A few targeted questions based on what you reported. Answering improves the assessment;
          you may skip any question.
        </p>

        {error && <div className="error-box">{error}</div>}

        <form onSubmit={handleSubmit}>
          {questions.map((q) => (
            <div className="field q-item" key={q}>
              <label htmlFor={`q-${q}`}>{q}</label>
              <input
                id={`q-${q}`}
                type="text"
                value={answers[q] ?? ''}
                onChange={(e) => setAnswers((prev) => ({ ...prev, [q]: e.target.value }))}
                placeholder="Type your answer…"
              />
            </div>
          ))}

          <div className="btn-row">
            <button type="button" className="btn btn-secondary" onClick={() => navigate('/symptoms')}>
              ← Back
            </button>
            <button className="btn btn-primary" type="submit" disabled={busy || questions.length === 0}>
              {busy ? 'Saving…' : 'Continue → Medical Report'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
