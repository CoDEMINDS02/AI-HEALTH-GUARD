import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Loader from '../components/Loader.jsx'
import RiskBadge from '../components/RiskBadge.jsx'
import { api } from '../services/api.js'

// Strip the [DEMO OUTPUT - ...] prefix for display. The stored value is unchanged.
function stripDemoPrefix(text) {
  return text.replace(/^\[DEMO OUTPUT[^\]]*\]\s*/i, '')
}

function formatDate(iso) {
  const date = new Date(iso)
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }) + ' · ' + date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
}

function HistoryCard({ item }) {
  const isDemo = /^\[DEMO OUTPUT/i.test(item.summary ?? '')
  const summary = stripDemoPrefix(item.summary ?? '')

  return (
    <article className="history-card">
      <div className="history-head">
        <RiskBadge level={item.risk_level} />
        {item.safety_override && (
          <span className="history-tag" title="The safety layer raised the risk level based on detected urgent warning signs.">
            ⚠ Safety escalation
          </span>
        )}
        {isDemo && <span className="history-tag">Demo</span>}
        <span className="history-date" style={{ marginLeft: 'auto' }}>{formatDate(item.created_at)}</span>
      </div>
      <p className="history-summary">
        {summary.length > 180 ? `${summary.slice(0, 180)}…` : summary}
      </p>
      <div className="history-actions">
        <Link to={`/results/${item.id}`} className="btn btn-ghost">View assessment →</Link>
      </div>
    </article>
  )
}

export default function HistoryPage() {
  const [items, setItems] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    api
      .listAnalyses()
      .then((data) => {
        if (!cancelled) setItems(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [])

  if (error) {
    return (
      <div className="card">
        <h2>Could not load history</h2>
        <div className="error-box" role="alert">{error}</div>
      </div>
    )
  }

  if (!items) {
    return (
      <div className="card">
        <Loader title="Analysis history" message="Loading your past assessments…" />
      </div>
    )
  }

  return (
    <div className="fade-in">
      <div className="card">
        <h2>Analysis history</h2>
        <p style={{ color: 'var(--text-2)' }}>
          Your completed preliminary assessments, most recent first.
        </p>

        {items.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon" aria-hidden="true">📋</div>
            <h3>No assessments yet</h3>
            <p>When you complete a health assessment, it will appear here for you to review.</p>
            <Link to="/profile" className="btn btn-primary">Start an assessment</Link>
          </div>
        ) : (
          <div className="history-list">
            {items.map((item) => (
              <HistoryCard key={item.id} item={item} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
