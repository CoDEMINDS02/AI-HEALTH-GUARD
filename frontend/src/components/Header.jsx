import { Link } from 'react-router-dom'
import { useDemoMode } from '../hooks/useDemoMode.js'

export default function Header() {
  const { demoMode, ready } = useDemoMode()

  return (
    <header className="header">
      <div className="header-inner">
        <Link to="/" className="brand">
          <span className="brand-mark" aria-hidden="true">✚</span>
          <span>
            AI HealthGuard
            <span className="brand-sub">Preliminary Health Analysis Assistant</span>
          </span>
        </Link>
        <nav className="header-nav">
          {ready && demoMode && (
            <span className="demo-chip" title="All AI outputs are synthetic and for demonstration only.">
              DEMO MODE
            </span>
          )}
          <Link to="/history">History</Link>
        </nav>
      </div>
    </header>
  )
}
