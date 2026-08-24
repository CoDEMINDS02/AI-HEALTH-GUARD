export default function Loader({ message = 'Working…' }) {
  return (
    <div className="loading-wrap">
      <div className="spinner" aria-hidden="true" />
      <p>{message}</p>
    </div>
  )
}
