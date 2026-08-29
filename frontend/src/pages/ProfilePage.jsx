import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Stepper from '../components/Stepper.jsx'
import { api } from '../services/api.js'
import { useFlow } from '../context/FlowContext.jsx'

export default function ProfilePage() {
  const navigate = useNavigate()
  const { startSession, profileDraft, setProfileDraft } = useFlow()

  const [age, setAge] = useState(profileDraft?.age ?? '')
  const [sex, setSex] = useState(profileDraft?.sex ?? 'prefer_not_to_say')
  const [conditions, setConditions] = useState(profileDraft?.conditions ?? '')
  const [allergies, setAllergies] = useState(profileDraft?.allergies ?? '')
  const [medications, setMedications] = useState(profileDraft?.medications ?? '')
  const [history, setHistory] = useState(profileDraft?.history ?? '')
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  const toList = (text) => text.split(',').map((s) => s.trim()).filter(Boolean)

  function updateDraft(field, value) {
    setProfileDraft({ age, sex, conditions, allergies, medications, history, [field]: value })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    if (!age || Number(age) < 1 || Number(age) > 120) {
      setError('Please enter a valid age between 1 and 120.')
      return
    }
    setBusy(true)
    try {
      const bundle = await api.createProfile({
        age: Number(age),
        sex,
        conditions: toList(conditions),
        allergies: toList(allergies),
        medications: toList(medications),
        history: history.trim() || null,
      })
      startSession(bundle.profile_id, bundle.session_id)
      navigate('/symptoms')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="fade-in">
      <Stepper current={0} />
      <div className="card">
        <h2>Tell us about yourself</h2>
        <p style={{ color: 'var(--text-2)' }}>
          A little context helps tailor the assessment. No name, address, or contact details —
          this information stays on your device.
        </p>

        {error && <div className="error-box" role="alert">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-section">
            <div className="form-section-title">About you</div>
            <div className="form-grid">
              <div className="field">
                <label htmlFor="age">Age</label>
                <input id="age" type="number" min="1" max="120" value={age}
                       onChange={(e) => { setAge(e.target.value); updateDraft('age', e.target.value) }}
                       placeholder="e.g. 34" required />
              </div>
              <div className="field">
                <label htmlFor="sex">Sex / gender</label>
                <select id="sex" value={sex} onChange={(e) => { setSex(e.target.value); updateDraft('sex', e.target.value) }}>
                  <option value="female">Female</option>
                  <option value="male">Male</option>
                  <option value="other">Other</option>
                  <option value="prefer_not_to_say">Prefer not to say</option>
                </select>
              </div>
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-title">Medical background <span className="hint" style={{ textTransform: 'none', letterSpacing: 0 }}>(all optional)</span></div>
            <div className="field">
              <label htmlFor="conditions">Known medical conditions <span className="hint">(comma separated)</span></label>
              <input id="conditions" type="text" value={conditions}
                     onChange={(e) => { setConditions(e.target.value); updateDraft('conditions', e.target.value) }}
                     placeholder="e.g. asthma, type 2 diabetes — or leave blank" />
            </div>
            <div className="field">
              <label htmlFor="allergies">Allergies <span className="hint">(comma separated)</span></label>
              <input id="allergies" type="text" value={allergies}
                     onChange={(e) => { setAllergies(e.target.value); updateDraft('allergies', e.target.value) }}
                     placeholder="e.g. penicillin, peanuts — or leave blank" />
            </div>
            <div className="field">
              <label htmlFor="medications">Current medications <span className="hint">(comma separated)</span></label>
              <input id="medications" type="text" value={medications}
                     onChange={(e) => { setMedications(e.target.value); updateDraft('medications', e.target.value) }}
                     placeholder="e.g. metformin — or leave blank" />
            </div>
            <div className="field">
              <label htmlFor="history">Other relevant medical history <span className="hint">(optional)</span></label>
              <textarea id="history" value={history}
                        onChange={(e) => { setHistory(e.target.value); updateDraft('history', e.target.value) }}
                        placeholder="Surgeries, family history, recent travel…" />
            </div>
          </div>

          <div className="btn-row">
            <button
              type="button"
              className="btn btn-secondary"
              aria-label="Go back to previous step"
              onClick={() => navigate('/')}
            >
              ← Back
            </button>
            <button className="btn btn-primary" type="submit" disabled={busy}>
              {busy ? 'Saving…' : 'Continue → Symptoms'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
