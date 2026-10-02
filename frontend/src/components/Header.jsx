import { Link } from 'react-router-dom'
import { useDemoMode } from '../hooks/useDemoMode.js'
import { useLang } from '../context/LanguageContext.jsx'

export default function Header() {
  const { demoMode, ready } = useDemoMode()
  const { t, toggleLang } = useLang()

  return (
    <header className="header">
      <div className="header-inner">
        <Link to="/" className="brand">
          <span className="brand-mark" aria-hidden="true">{'\u271A'}</span>
          <span>
            AI HealthGuard
            <span className="brand-sub">{t('brandSub')}</span>
          </span>
        </Link>
        <nav className="header-nav">
          {ready && demoMode && (
            <span className="demo-chip" title={t('demoModeTitle')}>
              {t('demoMode')}
            </span>
          )}
          <Link to="/history">{t('history')}</Link>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={toggleLang}
            title={t('switchTitle')}
            style={{ padding: '4px 12px', fontSize: 13 }}
          >
            {t('switchLabel')}
          </button>
        </nav>
      </div>
    </header>
  )
}