import { Link, useNavigate } from 'react-router-dom'
import { useLang } from '../context/LanguageContext.jsx'

const FEATURES = [
  { icon: '\u{1FA7A}', titleKey: 'feat1Title', textKey: 'feat1Text' },
  { icon: '\u2753', titleKey: 'feat2Title', textKey: 'feat2Text' },
  { icon: '\u{1F4C4}', titleKey: 'feat3Title', textKey: 'feat3Text' },
  { icon: '\u{1F6E1}\uFE0F', titleKey: 'feat4Title', textKey: 'feat4Text' },
]

const TRUST_KEYS = ['trust1', 'trust2', 'trust3']

const HOW_KEYS = ['how1', 'how2', 'how3', 'how4', 'how5']

export default function LandingPage() {
  const navigate = useNavigate()
  const { t } = useLang()

  return (
    <div className="fade-in">
      <div className="hero">
        <span className="hero-badge">{t('heroBadge')}</span>
        <h1>{t('heroTitle')}</h1>
        <p className="lead">{t('heroLead')}</p>
        <p className="hero-sub">{t('heroSub')}</p>

        <div className="hero-cta">
          <button className="btn btn-primary btn-lg" onClick={() => navigate('/profile')}>
            {t('startBtn')}
          </button>
          <Link to="/history" className="btn btn-secondary btn-lg">
            {t('viewPast')}
          </Link>
        </div>

        <div className="trust-row">
          {TRUST_KEYS.map((key) => (
            <span className="trust-item" key={key}>
              <span className="tick" aria-hidden="true">{'\u2713'}</span>
              {t(key)}
            </span>
          ))}
        </div>

        <div className="feature-grid">
          {FEATURES.map((f) => (
            <div className="feature" key={f.titleKey}>
              <div className="icon" aria-hidden="true">{f.icon}</div>
              <h3>{t(f.titleKey)}</h3>
              <p>{t(f.textKey)}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h2>{t('howTitle')}</h2>
        <ol className="steps-list">
          {HOW_KEYS.map((key) => (
            <li key={key}>{t(key)}</li>
          ))}
        </ol>
      </div>
    </div>
  )
}