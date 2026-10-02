import { useLang } from '../context/LanguageContext.jsx'

const STEP_KEYS = ['stepProfile', 'stepSymptoms', 'stepQuestions', 'stepReport', 'stepResults']

export default function Stepper({ current }) {
  const { t } = useLang()

  return (
    <nav className="stepper" aria-label={t('stepperAria')}>
      {STEP_KEYS.map((key, index) => {
        const label = t(key)
        const state = index < current ? 'done' : index === current ? 'active' : ''
        return (
          <span key={key} className={`step ${state}`} aria-current={index === current ? 'step' : undefined}>
            <span className="step-num" aria-hidden="true">{index < current ? '✓' : index + 1}</span>
            <span className="step-label">{label}</span>
          </span>
        )
      })}
    </nav>
  )
}