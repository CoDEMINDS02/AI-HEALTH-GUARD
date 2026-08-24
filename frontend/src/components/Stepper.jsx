const STEPS = ['Profile', 'Symptoms', 'Follow-up', 'Report', 'Results']

export default function Stepper({ current }) {
  return (
    <div className="stepper" aria-label="Assessment progress">
      {STEPS.map((label, index) => {
        const state = index < current ? 'done' : index === current ? 'active' : ''
        return (
          <span key={label} className={`step ${state}`}>
            <span className="step-num">{index < current ? '✓' : index + 1}</span>
            {label}
          </span>
        )
      })}
    </div>
  )
}
