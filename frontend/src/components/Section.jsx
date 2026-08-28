export default function Section({ title, subtitle, children, span2 = false }) {
  return (
    <div className={`card ${span2 ? 'span-2' : ''}`}>
      <div className="section-label">{title}</div>
      {subtitle && <p className="section-sub">{subtitle}</p>}
      {children}
    </div>
  )
}
