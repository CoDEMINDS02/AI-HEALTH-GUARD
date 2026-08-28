export default function Loader({ message = 'Working…', title }) {
  return (
    <div className="loading-wrap" role="status" aria-live="polite">
      <div className="spinner" aria-hidden="true" />
      {title && <div className="loading-title">{title}</div>}
      <div className="loading-sub">{message}</div>
    </div>
  )
}
