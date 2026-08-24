export default function RiskBadge({ level }) {
  return (
    <span className={`risk-badge risk-${level}`}>
      <span className="risk-dot" aria-hidden="true" />
      {level} RISK
    </span>
  )
}
