import { useNavigate } from 'react-router-dom'

const FEATURES = [
  {
    icon: '🩺',
    title: 'Symptom Understanding',
    text: 'Describe how you feel in plain language. HealthGuard organizes duration, severity, and onset into a clear picture.',
  },
  {
    icon: '❓',
    title: 'Smart Follow-up Questions',
    text: 'A small set of relevant clarifying questions, so the assessment reflects what matters.',
  },
  {
    icon: '📄',
    title: 'Medical Report Reading',
    text: 'Upload a lab report PDF. Extracted values keep their units and reference ranges — nothing is invented.',
  },
  {
    icon: '🛡️',
    title: 'Safety-First Risk Layer',
    text: 'A deterministic safety engine checks for urgent warning signs before anything else is shown.',
  },
]

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div>
      <div className="hero">
        <span className="hero-badge">PRELIMINARY · NOT A DIAGNOSIS</span>
        <h1>Understand your symptoms before your next appointment</h1>
        <p className="lead">
          AI HealthGuard turns what you report — symptoms, context, and optional medical reports —
          into an organized preliminary health summary with clear next-step guidance. It never
          diagnoses, prescribes, or replaces a doctor.
        </p>
        <button className="btn btn-primary" onClick={() => navigate('/profile')}>
          Start a Health Assessment
        </button>

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

      <div className="card" style={{ marginTop: 18 }}>
        <h2>How it works</h2>
        <ol style={{ margin: '6px 0 0', paddingLeft: 20 }}>
          <li>Tell us a little about your general health profile.</li>
          <li>Describe what you are experiencing and how severe it feels.</li>
          <li>Answer a few targeted follow-up questions.</li>
          <li>Optionally attach a medical report (PDF).</li>
          <li>Receive a structured preliminary summary with risk level, possible concerns, and questions to bring to a healthcare professional.</li>
        </ol>
      </div>
    </div>
  )
}
