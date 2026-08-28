const STEPS = ['Profile', 'Symptoms', 'Questions', 'Report', 'Results']

export default function Stepper({ current }) {
  return (
    <nav className="stepper" aria-label="Assessment progress">
      {STEPS.map((label, index) => {
        const state = index < current ? 'done' : index === current ? 'active' : ''
        return (
          <span key={label} className={`step ${state}`} aria-current={index === current ? 'step' : undefined}>
            <span className="step-num" aria-hidden="true">{index < current ? '✓' : index + 1}</span>
            <span className="step-label">{label}</span>
          </span>
        )
      })}
    </nav>
  )
}
