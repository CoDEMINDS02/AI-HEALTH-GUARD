import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import RiskBadge from '../components/RiskBadge.jsx'
import Section from '../components/Section.jsx'
import Loader from '../components/Loader.jsx'
import Stepper from '../components/Stepper.jsx'
import { api } from '../services/api.js'
import { useFlow } from '../context/FlowContext.jsx'

function List({ items, marker = '•' }) {
  if (!items?.length) return <p style={{ color: 'var(--muted)' }}>Nothing reported.</p>
  return (
    <ul className="list-check">
      {items.map((item, i) => (
        <li key={i}>
          <span className="marker" aria-hidden="true">{marker}</span>
          <span>{item}</span>
        </li>
      ))}
    </ul>
  )
}

export default function ResultsPage() {
  const { analysisId } = useParams()
  const navigate = useNavigate()
  const { reset } = useFlow()

  const [analysis, setAnalysis] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    const id = Number(analysisId)
    if (!Number.isFinite(id)) {
      setError('Invalid analysis reference.')
      return
    }
    api
      .getAnalysis(id)
      .then((data) => {
        if (!cancelled) setAnalysis(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [analysisId])

  function startNew() {
    reset()
    navigate('/profile')
  }

  if (error) {
    return (
      <div className="card">
        <h2>Could not load the assessment</h2>
        <div className="error-box">{error}</div>
        <button className="btn btn-secondary" onClick={startNew}>Start a new assessment</button>
      </div>
    )
  }

  if (!analysis) {
    return (
      <div className="card">
        <Loader message="Loading your assessment…" />
      </div>
    )
  }

  return (
    <div>
      <Stepper current={4} />

      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap' }}>
          <h2 style={{ margin: 0 }}>Preliminary health summary</h2>
          <RiskBadge level={analysis.risk_level} />
          {analysis.safety_override && (
            <span className="demo-chip">SAFETY ESCALATION APPLIED</span>
          )}
          {analysis.source === 'demo' && (
            <span className="demo-chip">DEMO OUTPUT — SYNTHETIC</span>
          )}
        </div>

        {analysis.risk_level === 'HIGH' && (
          <div className="alert alert-HIGH" style={{ marginTop: 14 }}>
            <strong>Urgent care may be needed.</strong> Based on what you described, please seek
            medical attention promptly. If symptoms are severe or worsening right now, contact
            local emergency services.
          </div>
        )}

        <p style={{ marginTop: 14 }}>{analysis.summary}</p>

        {analysis.symptoms.length > 0 && (
          <>
            <div className="section-label" style={{ marginTop: 12 }}>Symptoms you reported</div>
            <div className="chips">
              {analysis.symptoms.map((s, i) => <span className="chip" key={i}>{s}</span>)}
            </div>
          </>
        )}
      </div>

      <div className="results-grid">
        {analysis.red_flags.length > 0 && (
          <Section title="Red flags detected" span2>
            <div className="alert alert-HIGH" style={{ marginBottom: 0 }}>
              These are urgent warning signs found in what you entered:
              <ul>
                {analysis.red_flags.map((flag, i) => <li key={i}>{flag}</li>)}
              </ul>
            </div>
          </Section>
        )}

        <Section title="Observations">
          <List items={analysis.observations} />
        </Section>

        <Section title="Possible concerns (not diagnoses)">
          <List items={analysis.possible_concerns} />
        </Section>

        <Section title="Recommended next steps" span2>
          <List items={analysis.recommended_next_steps} marker="→" />
        </Section>

        <Section title="Questions for your doctor">
          <List items={analysis.questions_for_doctor} marker="?" />
        </Section>

        <Section title="Limitations of this assessment">
          <p>{analysis.limitations}</p>
        </Section>
      </div>

      <div className="card">
        <div className="alert alert-warn" style={{ marginBottom: 12 }}>{analysis.disclaimer}</div>
        <div className="btn-row" style={{ marginTop: 0 }}>
          <Link to="/history" className="btn btn-secondary">View history</Link>
          <button className="btn btn-primary" onClick={startNew}>Start new assessment</button>
        </div>
      </div>
    </div>
  )
}
