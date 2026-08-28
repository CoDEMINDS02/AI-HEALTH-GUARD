import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Loader from '../components/Loader.jsx'
import Section from '../components/Section.jsx'
import Stepper from '../components/Stepper.jsx'
import { useFlow } from '../context/FlowContext.jsx'
import { api } from '../services/api.js'

// Maps a finding flag to its CSS class and display label.
const FLAG_META = {
  high:     { cls: 'flag-high',     label: 'HIGH' },
  low:      { cls: 'flag-low',      label: 'LOW' },
  abnormal: { cls: 'flag-abnormal', label: 'ABNORMAL' },
  normal:   { cls: 'flag-normal',   label: 'Normal' },
  unknown:  { cls: 'flag-unknown',  label: '—' },
}

function FindingFlag({ flag }) {
  const meta = FLAG_META[flag] ?? FLAG_META.unknown
  return <span className={meta.cls}>{meta.label}</span>
}

function FindingsTable({ findings }) {
  if (!findings?.length) return null
  return (
    <table className="report-table" aria-label="Extracted laboratory findings">
      <thead>
        <tr>
          <th>Test</th>
          <th>Value</th>
          <th>Unit</th>
          <th>Reference range</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {findings.map((row, i) => (
          <tr key={i}>
            <td>{row.name}</td>
            <td style={{ fontFamily: 'monospace' }}>{row.value}</td>
            <td style={{ color: 'var(--muted)' }}>{row.unit ?? '—'}</td>
            <td style={{ color: 'var(--muted)' }}>{row.reference_range ?? '—'}</td>
            <td><FindingFlag flag={row.flag} /></td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function ReportNotes({ notes }) {
  if (!notes?.length) return null
  return (
    <div style={{ marginTop: 14 }}>
      <div className="section-label">Impression / notes</div>
      <ul className="list-check">
        {notes.map((n, i) => (
          <li key={i}>
            <span className="marker" aria-hidden="true">•</span>
            <span>{n}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

function ReportSummary({ summary }) {
  if (!summary) return null
  return (
    <p style={{ color: 'var(--muted)', fontSize: 13.5, marginTop: 8 }}>{summary}</p>
  )
}

function ExplainSection({ reportId }) {
  const [busy, setBusy] = useState(false)
  const [explanation, setExplanation] = useState(null)
  const [error, setError] = useState(null)

  async function handleExplain() {
    setBusy(true)
    setError(null)
    try {
      const data = await api.explainReport(reportId)
      setExplanation(data.explanation)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  if (explanation) {
    return (
      <div style={{ marginTop: 18 }}>
        <div className="section-label">AI plain-language explanation</div>
        <div className="alert alert-info" style={{ whiteSpace: 'pre-wrap', marginBottom: 0 }}>
          {explanation}
        </div>
      </div>
    )
  }

  return (
    <div style={{ marginTop: 14 }}>
      {busy && <Loader message="Generating plain-language explanation…" />}
      {error && <div className="error-box">{error}</div>}
      {!busy && (
        <button className="btn btn-secondary" onClick={handleExplain}>
          Explain this report in plain language
        </button>
      )}
    </div>
  )
}

function ReportFindings({ report }) {
  const findings = report.extracted_findings?.findings ?? []
  const notes = report.extracted_findings?.notes ?? []
  const summary = report.extracted_findings?.summary ?? ''

  if (report.status === 'stored_no_ocr') {
    return (
      <div className="alert alert-warn" style={{ marginTop: 14 }}>
        <strong>Image stored — text extraction not available.</strong> This file appears to be a
        scanned image or photo. OCR is not enabled in this prototype, so lab values could not be
        read automatically. Your symptom analysis will continue without report data. Please review
        this document directly with a healthcare professional.
      </div>
    )
  }

  if (report.status === 'extraction_failed') {
    return (
      <div className="alert alert-warn" style={{ marginTop: 14 }}>
        <strong>Text could not be extracted from this PDF.</strong> The file was uploaded
        successfully but its content could not be read (it may be password-protected or corrupted).
        Your symptom analysis will continue without report data.
      </div>
    )
  }

  if (report.status !== 'parsed' || findings.length === 0) {
    return (
      <div className="alert alert-warn" style={{ marginTop: 14 }}>
        No structured lab values were found in this document. Your analysis will continue using
        the symptom information you provided.
      </div>
    )
  }

  return (
    <div style={{ marginTop: 18 }}>
      <div className="section-label">
        Extracted findings — {findings.length} value{findings.length !== 1 ? 's' : ''} read
      </div>
      <ReportSummary summary={summary} />
      <FindingsTable findings={findings} />
      <ReportNotes notes={notes} />
      <ExplainSection reportId={report.id} />
    </div>
  )
}

export default function ReportPage() {
  const navigate = useNavigate()
  const { sessionId, setReportInfo } = useFlow()

  const [file, setFile] = useState(null)
  const [busy, setBusy] = useState(false)
  const [uploadMessage, setUploadMessage] = useState(null)
  const [isError, setIsError] = useState(false)
  const [report, setReport] = useState(null)

  async function handleUpload() {
    if (!file) return
    setBusy(true)
    setUploadMessage(null)
    setIsError(false)
    setReport(null)
    try {
      const data = await api.uploadReport(sessionId, file)
      const r = data.report
      setReportInfo(r)
      setReport(r)
      const isParsed = r.status === 'parsed'
      const findingCount = r.extracted_findings?.findings?.length ?? 0
      setUploadMessage(
        isParsed
          ? `Report uploaded. ${findingCount > 0 ? `${findingCount} lab value${findingCount !== 1 ? 's' : ''} extracted.` : 'No structured values found.'}`
          : data.message,
      )
      setIsError(!isParsed)
    } catch (err) {
      setUploadMessage(err.message)
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

        {uploadMessage && (
          <div className={isError ? 'alert alert-warn' : 'alert alert-info'}>
            {uploadMessage}
          </div>
        )}

        {busy && <Loader message="Reading report…" />}

        {!busy && (
          <>
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
                Skip — I don&apos;t have a report
              </button>
              <button
                className="btn btn-primary"
                disabled={!file}
                onClick={handleUpload}
              >
                {file ? 'Upload & Read' : 'Select a file first'}
              </button>
            </div>
          </>
        )}
      </div>

      {report && (
        <Section title="Report findings">
          <ReportFindings report={report} />
        </Section>
      )}

      <div className="btn-row btn-row-end" style={{ marginBottom: 24 }}>
        <button
          className="btn btn-secondary"
          onClick={() => navigate('/analyze')}
          disabled={busy}
        >
          Continue → Analysis
        </button>
      </div>
    </div>
  )
}
