export default function Section({ title, children, span2 = false }) {
  return (
    <div className={`card ${span2 ? 'span-2' : ''}`}>
      <div className="section-label">{title}</div>
      {children}
    </div>
  )
}
