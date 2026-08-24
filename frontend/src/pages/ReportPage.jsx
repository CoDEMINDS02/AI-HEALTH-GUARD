import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Stepper from '../components/Stepper.jsx'
import { api } from '../services/api.js'
import { useFlow } from '../context/FlowContext.jsx'

export default function ReportPage() {
  const navigate = useNavigate()
  const { sessionId, setReportInfo } = useFlow()

  const [file, setFile] = useState(null)
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState(null)
  const [isError, setIsError] = useState(false)

  async function handleUpload() {
    if (!file) return
    setBusy(true)
    setMessage(null)
    setIsError(false)
    try {
      const data = await api.uploadReport(sessionId, file)
      const report = data.report
      setReportInfo(report)
      const findingCount =
        report.extracted_findings?.findings?.length ?? 0
      setMessage(
        report.status === 'parsed'
          ? `✅ ${data.message} ${findingCount > 0 ? 'Values below were read exactly as written.' : ''}`
          : `⚠️ ${data.message}`,
      )
      setIsError(report.status !== 'parsed')
    } catch (err) {
      setMessage(`⚠️ ${err.message}`)
      setIsError(true)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <Stepper current={3} />
      <div className="card">
        <h2>Medical report (optional)</h2>
        <p style={{ color: 'var(--muted)' }}>
          Upload a lab report PDF and HealthGuard will extract structured values with their units
          and reference ranges. Images are accepted but OCR is not enabled in this prototype.
          Nothing is invented — if text cannot be read, you will be told clearly.
        </p>

        {message && (
          <div className={isError ? 'alert alert-warn' : 'alert alert-info'}>{message}</div>
        )}

        <div className="field">
          <label htmlFor="file">Choose a file (PDF or image, max 10 MB)</label>
          <input
            id="file"
            type="file"
            accept=".pdf,.png,.jpg,.jpeg,.webp,application/pdf,image/png,image/jpeg,image/webp"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </div>

        <div className="btn-row">
          <button className="btn btn-secondary" onClick={() => navigate('/analyze')}>
            Skip — I don't have a report
          </button>
          <button className="btn btn-primary" disabled={!file || busy} onClick={handleUpload}>
            {busy ? 'Reading report…' : file ? 'Upload & Read' : 'Select a file first'}
          </button>
        </div>
      </div>

      <div className="btn-row btn-row-end" style={{ marginBottom: 24 }}>
        <button className="btn btn-secondary" onClick={() => navigate('/analyze')} disabled={busy}>
          Continue → Analysis
        </button>
      </div>
    </div>
  )
}
