import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Loader from '../components/Loader.jsx'
import RiskBadge from '../components/RiskBadge.jsx'
import { api } from '../services/api.js'

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
        <div className="error-box">{error}</div>
      </div>
    )
  }

  if (!items) {
    return <div className="card"><Loader message="Loading history…" /></div>
  }

  return (
    <div className="card">
      <h2>Analysis history</h2>
      {items.length === 0 ? (
        <p style={{ color: 'var(--muted)' }}>
          No assessments yet.{' '}
          <Link to="/profile">Start your first assessment</Link>.
        </p>
      ) : (
        <table className="history-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Risk</th>
              <th>Summary</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td style={{ whiteSpace: 'nowrap' }}>
                  {new Date(item.created_at).toLocaleString()}
                </td>
                <td>
                  <RiskBadge level={item.risk_level} />
                </td>
                <td style={{ maxWidth: 420 }}>
                  {item.summary.length > 140 ? `${item.summary.slice(0, 140)}…` : item.summary}
                </td>
                <td>
                  <Link to={`/results/${item.id}`}>Open →</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
