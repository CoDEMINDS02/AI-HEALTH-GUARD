const RISK_META = {
  LOW: { sym: '✓', label: 'Low risk' },
  MODERATE: { sym: '▲', label: 'Moderate risk' },
  HIGH: { sym: '⚠', label: 'High risk' },
}

export default function RiskBadge({ level }) {
  const meta = RISK_META[level] ?? { sym: '—', label: level }
  return (
    <span className={`risk-badge risk-${level}`}>
      <span className="risk-sym" aria-hidden="true">{meta.sym}</span>
      {meta.label}
    </span>
  )
}
