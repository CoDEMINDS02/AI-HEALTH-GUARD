import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Stepper from '../components/Stepper.jsx'
import { api } from '../services/api.js'
import { useFlow } from '../context/FlowContext.jsx'

export default function SymptomsPage() {
  const navigate = useNavigate()
  const { sessionId, setQuestions } = useFlow()

  const [primary, setPrimary] = useState('')
  const [description, setDescription] = useState('')
  const [duration, setDuration] = useState('')
  const [severity, setSeverity] = useState(5)
  const [onset, setOnset] = useState('gradual')
  const [additional, setAdditional] = useState('')
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    if (!sessionId) {
      navigate('/profile')
      return
    }
    if (!primary.trim()) {
      setError('Please enter at least one primary symptom.')
      return
    }
    setBusy(true)
    try {
      await api.submitSymptoms({
        session_id: sessionId,
        primary_symptoms: primary,
        description,
        duration_text: duration || 'not specified',
        severity: Number(severity),
        onset,
        additional_symptoms: additional,
      })
      const followUp = await api.generateFollowUp(sessionId)
      setQuestions(followUp.questions ?? [])
      navigate('/follow-up')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <Stepper current={1} />
      <div className="card">
        <h2>Symptom assessment</h2>
        <p style={{ color: 'var(--muted)' }}>
          Example: “Fever, headache and weakness for 3 days.”
        </p>

        {error && <div className="error-box">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="primary">Primary symptoms <span className="hint">(comma separated)</span></label>
            <input id="primary" type="text" value={primary} onChange={(e) => setPrimary(e.target.value)}
                   placeholder="e.g. fever, headache" required />
          </div>

          <div className="field">
            <label htmlFor="description">Describe what you are feeling</label>
            <textarea id="description" value={description} onChange={(e) => setDescription(e.target.value)}
                      placeholder="When did it start? What does it feel like? Anything that makes it better or worse?" />
          </div>

          <div className="form-grid">
            <div className="field">
              <label htmlFor="duration">Duration</label>
              <input id="duration" type="text" value={duration} onChange={(e) => setDuration(e.target.value)}
                     placeholder="e.g. 3 days" />
            </div>
            <div className="field">
              <label htmlFor="onset">Onset</label>
              <select id="onset" value={onset} onChange={(e) => setOnset(e.target.value)}>
                <option value="sudden">Sudden</option>
                <option value="gradual">Gradual</option>
              </select>
            </div>
          </div>

          <div className="field">
            <label htmlFor="severity">Severity (1 = barely noticeable · 10 = unbearable)</label>
            <div className="range-wrap">
              <input id="severity" type="range" min="1" max="10" value={severity}
                     onChange={(e) => setSeverity(e.target.value)} />
              <span className="severity-value">{severity}/10</span>
            </div>
          </div>

          <div className="field">
            <label htmlFor="additional">Additional symptoms <span className="hint">(comma separated, optional)</span></label>
            <input id="additional" type="text" value={additional} onChange={(e) => setAdditional(e.target.value)}
                   placeholder="e.g. chills, sore throat" />
          </div>

          <div className="btn-row btn-row-end">
            <button className="btn btn-primary" type="submit" disabled={busy}>
              {busy ? 'Preparing questions…' : 'Continue → Follow-up Questions'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
