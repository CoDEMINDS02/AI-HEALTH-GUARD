import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Stepper from '../components/Stepper.jsx'
import { api } from '../services/api.js'
import { useFlow } from '../context/FlowContext.jsx'
import { useLang } from '../context/LanguageContext.jsx'

export default function ProfilePage() {
  const navigate = useNavigate()
  const { startSession, profileDraft, setProfileDraft } = useFlow()
  const { t, lang } = useLang()

  const [age, setAge] = useState(profileDraft?.age ?? '')
  const [sex, setSex] = useState(profileDraft?.sex ?? 'prefer_not_to_say')
  const [conditions, setConditions] = useState(profileDraft?.conditions ?? '')
  const [allergies, setAllergies] = useState(profileDraft?.allergies ?? '')
  const [medications, setMedications] = useState(profileDraft?.medications ?? '')
  const [history, setHistory] = useState(profileDraft?.history ?? '')
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  const toList = (text) => text.split(/[,\u060C]/).map((s) => s.trim()).filter(Boolean)

  function updateDraft(field, value) {
    setProfileDraft({ age, sex, conditions, allergies, medications, history, [field]: value })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    if (!age || Number(age) < 1 || Number(age) > 120) {
      setError(t('profileAgeError'))
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

  const backArrow = lang === 'ur' ? '\u2192' : '\u2190'
  const nextArrow = lang === 'ur' ? '\u2190' : '\u2192'

  return (
    <div className="fade-in">
      <Stepper current={0} />
      <div className="card">
        <h2>{t('profileTitle')}</h2>
        <p style={{ color: 'var(--text-2)' }}>{t('profileIntro')}</p>

        {error && <div className="error-box" role="alert">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-section">
            <div className="form-section-title">{t('profileAboutYou')}</div>
            <div className="form-grid">
              <div className="field">
                <label htmlFor="age">{t('profileAge')}</label>
                <input id="age" type="number" min="1" max="120" value={age}
                       onChange={(e) => { setAge(e.target.value); updateDraft('age', e.target.value) }}
                       placeholder={t('profileAgePlaceholder')} required />
              </div>
              <div className="field">
                <label htmlFor="sex">{t('profileSex')}</label>
                <select id="sex" value={sex} onChange={(e) => { setSex(e.target.value); updateDraft('sex', e.target.value) }}>
                  <option value="female">{t('profileFemale')}</option>
                  <option value="male">{t('profileMale')}</option>
                  <option value="other">{t('profileOther')}</option>
                  <option value="prefer_not_to_say">{t('profilePreferNot')}</option>
                </select>
              </div>
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-title">
              {t('profileMedical')}{' '}
              <span className="hint" style={{ textTransform: 'none', letterSpacing: 0 }}>{t('profileAllOptional')}</span>
            </div>
            <p className="hint" style={{ marginTop: 0, marginBottom: 12 }}>
              {t('profileLeaveEmpty')}
            </p>
            <div className="field">
              <label htmlFor="conditions">{t('profileConditions')} <span className="hint">{t('profileCommaSep')}</span></label>
              <input id="conditions" type="text" value={conditions}
                     onChange={(e) => { setConditions(e.target.value); updateDraft('conditions', e.target.value) }}
                     placeholder={t('profileConditionsPh')} />
            </div>
            <div className="field">
              <label htmlFor="allergies">{t('profileAllergies')} <span className="hint">{t('profileCommaSep')}</span></label>
              <input id="allergies" type="text" value={allergies}
                     onChange={(e) => { setAllergies(e.target.value); updateDraft('allergies', e.target.value) }}
                     placeholder={t('profileAllergiesPh')} />
            </div>
            <div className="field">
              <label htmlFor="medications">{t('profileMedications')} <span className="hint">{t('profileCommaSep')}</span></label>
              <input id="medications" type="text" value={medications}
                     onChange={(e) => { setMedications(e.target.value); updateDraft('medications', e.target.value) }}
                     placeholder={t('profileMedicationsPh')} />
            </div>
            <div className="field">
              <label htmlFor="history">{t('profileHistory')} <span className="hint">{t('profileOptional')}</span></label>
              <textarea id="history" value={history}
                        onChange={(e) => { setHistory(e.target.value); updateDraft('history', e.target.value) }}
                        placeholder={t('profileHistoryPh')} />
            </div>
          </div>

          <div className="btn-row">
            <button
              type="button"
              className="btn btn-secondary"
              aria-label={t('profileBackAria')}
              onClick={() => navigate('/')}
            >
              {backArrow} {t('profileBack')}
            </button>
            <button className="btn btn-primary" type="submit" disabled={busy}>
              {busy ? t('profileSaving') : `${t('profileContinue')} ${nextArrow} ${t('profileSymptoms')}`}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}