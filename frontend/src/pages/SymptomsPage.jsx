import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Stepper from '../components/Stepper.jsx'
import { api } from '../services/api.js'
import { useFlow } from '../context/FlowContext.jsx'
import { useLang } from '../context/LanguageContext.jsx'

const normalizeCommas = (text) => text.replace(/\u060C/g, ',')

export default function SymptomsPage() {
  const navigate = useNavigate()
  const { sessionId, setQuestions, symptomDraft, setSymptomDraft } = useFlow()
  const { t, lang } = useLang()

  const [primary, setPrimary] = useState(symptomDraft?.primary ?? '')
  const [description, setDescription] = useState(symptomDraft?.description ?? '')
  const [duration, setDuration] = useState(symptomDraft?.duration ?? '')
  const [severity, setSeverity] = useState(symptomDraft?.severity ?? 5)
  const [onset, setOnset] = useState(symptomDraft?.onset ?? 'gradual')
  const [additional, setAdditional] = useState(symptomDraft?.additional ?? '')
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  function updateDraft(field, value) {
    setSymptomDraft({ primary, description, duration, severity, onset, additional, [field]: value })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    if (!sessionId) {
      navigate('/profile')
      return
    }
    if (!primary.trim()) {
      setError(t('symNeedOne'))
      return
    }
    setBusy(true)
    try {
      await api.submitSymptoms({
        session_id: sessionId,
        primary_symptoms: normalizeCommas(primary),
        description,
        duration_text: duration || 'not specified',
        severity: Number(severity),
        onset,
        additional_symptoms: normalizeCommas(additional),
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

  const backArrow = lang === 'ur' ? '\u2192' : '\u2190'
  const nextArrow = lang === 'ur' ? '\u2190' : '\u2192'

  return (
    <div className="fade-in">
      <Stepper current={1} />
      <div className="card">
        <h2>{t('symTitle')}</h2>
        <p style={{ color: 'var(--text-2)' }}>{t('symIntro')}</p>

        {error && <div className="error-box" role="alert">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-section">
            <div className="form-section-title">{t('symYour')}</div>
            <div className="field">
              <label htmlFor="primary">{t('symPrimary')} <span className="hint">{t('profileCommaSep')}</span></label>
              <input id="primary" type="text" value={primary}
                     onChange={(e) => { setPrimary(e.target.value); updateDraft('primary', e.target.value) }}
                     placeholder={t('symPrimaryPh')} required />
            </div>

            <div className="field">
              <label htmlFor="description">{t('symDescribe')}</label>
              <textarea id="description" value={description}
                        onChange={(e) => { setDescription(e.target.value); updateDraft('description', e.target.value) }}
                        placeholder={t('symDescribePh')} />
            </div>

            <div className="field">
              <label htmlFor="additional">{t('symAdditional')} <span className="hint">{t('symCommaOptional')}</span></label>
              <input id="additional" type="text" value={additional}
                     onChange={(e) => { setAdditional(e.target.value); updateDraft('additional', e.target.value) }}
                     placeholder={t('symAdditionalPh')} />
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-title">{t('symDetails')}</div>
            <div className="form-grid">
              <div className="field">
                <label htmlFor="duration">{t('symDuration')}</label>
                <input id="duration" type="text" value={duration}
                       onChange={(e) => { setDuration(e.target.value); updateDraft('duration', e.target.value) }}
                       placeholder={t('symDurationPh')} />
              </div>
              <div className="field">
                <label htmlFor="onset">{t('symOnset')}</label>
                <select id="onset" value={onset}
                        onChange={(e) => { setOnset(e.target.value); updateDraft('onset', e.target.value) }}>
                  <option value="sudden">{t('symSudden')}</option>
                  <option value="gradual">{t('symGradual')}</option>
                </select>
              </div>
            </div>

            <div className="field">
              <label htmlFor="severity">
                {t('symSeverity')} <span className="hint">{t('symSeverityHint')}</span>
              </label>
              <div className="range-wrap">
                <input id="severity" type="range" min="1" max="10" value={severity}
                       onChange={(e) => { setSeverity(e.target.value); updateDraft('severity', e.target.value) }}
                       aria-valuetext={`${severity}/10`} />
                <span className="severity-value">{severity}/10</span>
              </div>
              <div className="range-labels" aria-hidden="true">
                <span>{t('symMild')}</span>
                <span>{t('symSevere')}</span>
              </div>
            </div>
          </div>

          <div className="btn-row">
            <button
              type="button"
              className="btn btn-secondary"
              aria-label={t('profileBackAria')}
              onClick={() => navigate('/profile')}
            >
              {backArrow} {t('profileBack')}
            </button>
            <button className="btn btn-primary" type="submit" disabled={busy}>
              {busy ? t('symPreparing') : `${t('profileContinue')} ${nextArrow} ${t('symFollowUp')}`}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}