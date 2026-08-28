import { Link, useNavigate } from 'react-router-dom'

const FEATURES = [
  {
    icon: '🩺',
    title: 'Symptom understanding',
    text: 'Describe how you feel in plain language. HealthGuard organizes duration, severity, and onset into a clear picture.',
  },
  {
    icon: '❓',
    title: 'Smart follow-up questions',
    text: 'A small set of relevant clarifying questions, so the assessment reflects what matters.',
  },
  {
    icon: '📄',
    title: 'Medical report reading',
    text: 'Upload a lab report PDF. Extracted values keep their units and reference ranges — nothing is invented.',
  },
  {
    icon: '🛡️',
    title: 'Safety-first risk layer',
    text: 'A deterministic safety engine checks every result for urgent warning signs before anything else is shown.',
  },
]

const TRUST_POINTS = [
  'Not a diagnosis',
  'Educational prototype',
  'Your data stays local',
]

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div className="fade-in">
      <div className="hero">
        <span className="hero-badge">Preliminary health information · Not a diagnosis</span>
        <h1>Understand your health information</h1>
        <p className="lead">
          Identify potential warning signs. Prepare better questions for your healthcare
          professional.
        </p>
        <p className="hero-sub">
          AI HealthGuard turns what you report — symptoms, context, and an optional medical
          report — into an organized preliminary summary with clear next-step guidance. It never
          diagnoses, prescribes, or replaces a doctor.
        </p>

        <div className="hero-cta">
          <button className="btn btn-primary btn-lg" onClick={() => navigate('/profile')}>
            Start Health Assessment
          </button>
          <Link to="/history" className="btn btn-secondary btn-lg">
            View past assessments
          </Link>
        </div>

        <div className="trust-row">
          {TRUST_POINTS.map((point) => (
            <span className="trust-item" key={point}>
              <span className="tick" aria-hidden="true">✓</span>
              {point}
            </span>
          ))}
        </div>

        <div className="feature-grid">
          {FEATURES.map((f) => (
            <div className="feature" key={f.title}>
              <div className="icon" aria-hidden="true">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.text}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h2>How it works</h2>
        <ol className="steps-list">
          <li>Tell us a little about your general health profile.</li>
          <li>Describe what you are experiencing and how severe it feels.</li>
          <li>Answer a few targeted follow-up questions.</li>
          <li>Optionally attach a medical report (PDF).</li>
          <li>
            Receive a structured preliminary summary with risk level, possible concerns, and
            questions to bring to a healthcare professional.
          </li>
        </ol>
      </div>
    </div>
  )
}
