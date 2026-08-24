import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Stepper from '../components/Stepper.jsx'
import { api } from '../services/api.js'
import { useFlow } from '../context/FlowContext.jsx'

export default function ProfilePage() {
  const navigate = useNavigate()
  const { startSession } = useFlow()

  const [age, setAge] = useState('')
  const [sex, setSex] = useState('prefer_not_to_say')
  const [conditions, setConditions] = useState('')
  const [allergies, setAllergies] = useState('')
  const [medications, setMedications] = useState('')
  const [history, setHistory] = useState('')
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  const toList = (text) => text.split(',').map((s) => s.trim()).filter(Boolean)

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
    <div>
      <Stepper current={0} />
      <div className="card">
        <h2>Health profile</h2>
        <p style={{ color: 'var(--muted)' }}>
          Only what is needed to contextualize your symptoms. No name, address, or contact details.
        </p>

        {error && <div className="error-box">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="field">
              <label htmlFor="age">Age</label>
              <input id="age" type="number" min="1" max="120" value={age}
                     onChange={(e) => setAge(e.target.value)} placeholder="e.g. 34" required />
            </div>
            <div className="field">
              <label htmlFor="sex">Sex / gender</label>
              <select id="sex" value={sex} onChange={(e) => setSex(e.target.value)}>
                <option value="female">Female</option>
                <option value="male">Male</option>
                <option value="other">Other</option>
                <option value="prefer_not_to_say">Prefer not to say</option>
              </select>
            </div>
          </div>

          <div className="field">
            <label htmlFor="conditions">Known medical conditions <span className="hint">(comma separated)</span></label>
            <input id="conditions" type="text" value={conditions} onChange={(e) => setConditions(e.target.value)}
                   placeholder="e.g. asthma, type 2 diabetes — or leave blank" />
          </div>
          <div className="field">
            <label htmlFor="allergies">Allergies <span className="hint">(comma separated)</span></label>
            <input id="allergies" type="text" value={allergies} onChange={(e) => setAllergies(e.target.value)}
                   placeholder="e.g. penicillin, peanuts — or leave blank" />
          </div>
          <div className="field">
            <label htmlFor="medications">Current medications <span className="hint">(comma separated)</span></label>
            <input id="medications" type="text" value={medications} onChange={(e) => setMedications(e.target.value)}
                   placeholder="e.g. metformin — or leave blank" />
          </div>
          <div className="field">
            <label htmlFor="history">Other relevant medical history <span className="hint">(optional)</span></label>
            <textarea id="history" value={history} onChange={(e) => setHistory(e.target.value)}
                      placeholder="Surgeries, family history, recent travel…" />
          </div>

          <div className="btn-row btn-row-end">
            <button className="btn btn-primary" type="submit" disabled={busy}>
              {busy ? 'Saving…' : 'Continue → Symptoms'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
