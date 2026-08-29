import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Loader from '../components/Loader.jsx'
import Stepper from '../components/Stepper.jsx'
import { useFlow } from '../context/FlowContext.jsx'
import { api } from '../services/api.js'

const FLAG_META = {
  high: { cls: 'status-high', sym: '↑', label: 'High' },
  low: { cls: 'status-low', sym: '↓', label: 'Low' },
  abnormal: { cls: 'status-abnormal', sym: '!', label: 'Abnormal' },
  normal: { cls: 'status-normal', sym: '✓', label: 'Normal' },
  unknown: { cls: 'status-unknown', sym: '—', label: 'Unknown' },
}

const ACCEPTED_EXTENSIONS = ['.pdf', '.png', '.jpg', '.jpeg', '.webp']

function formatSize(bytes) {
  if (bytes == null) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function FindingStatus({ flag }) {
  const meta = FLAG_META[flag] ?? FLAG_META.unknown
  return (
    <span className={`status ${meta.cls}`}>
      <span className="sym" aria-hidden="true">{meta.sym}</span>
      {meta.label}
    </span>
  )
}

function FindingsTable({ findings }) {
  if (!findings?.length) return null
  return (
    <div className="report-table-wrap">
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
              <td data-label="Test">{row.name}</td>
              <td data-label="Value" className="val">{row.value}</td>
              <td data-label="Unit" className="mut">{row.unit ?? '—'}</td>
              <td data-label="Reference range" className="mut">{row.reference_range ?? '—'}</td>
              <td data-label="Status"><FindingStatus flag={row.flag} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
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
        <div className="section-label">Plain-language explanation</div>
        <div className="explanation-block">{explanation}</div>
      </div>
    )
  }

  return (
    <div className="explain-btn-row">
      {busy && <Loader title="Explaining your report" message="Generating a plain-language explanation…" />}
      {error && <div className="error-box" role="alert">{error}</div>}
      {!busy && (
        <button className="btn btn-primary" onClick={handleExplain}>
          Explain this report in plain language
        </button>
      )}
    </div>
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

function ReportFindings({ report }) {
  const findings = report.extracted_findings?.findings ?? []
  const notes = report.extracted_findings?.notes ?? []
  const summary = report.extracted_findings?.summary ?? ''

  if (report.status === 'stored_no_ocr') {
    return (
      <div className="alert alert-warn" role="alert">
        <strong>Image stored — text extraction not available.</strong> This file appears to be a
        scanned image or photo. OCR is not enabled in this prototype, so lab values could not be
        read automatically. Your symptom analysis will continue without report data. Please review
        this document directly with a healthcare professional.
      </div>
    )
  }

  if (report.status === 'extraction_failed') {
    return (
      <div className="alert alert-warn" role="alert">
        <strong>Text could not be extracted from this PDF.</strong> The file was uploaded
        successfully but its content could not be read (it may be password-protected or
        corrupted). Your symptom analysis will continue without report data.
      </div>
    )
  }

  if (report.status !== 'parsed' || findings.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon" aria-hidden="true">📄</div>
        <h3>No structured lab values found</h3>
        <p>
          The document was read, but no laboratory-style values were recognized. Your analysis
          will continue using the symptom information you provided.
        </p>
      </div>
    )
  }

  return (
    <div>
      <div className="section-label">
        Extracted findings — {findings.length} value{findings.length !== 1 ? 's' : ''} read
      </div>
      {summary && <p className="section-sub">{summary}</p>}
      <FindingsTable findings={findings} />
      <ReportNotes notes={notes} />
      <ExplainSection reportId={report.id} />
    </div>
  )
}

export default function ReportPage() {
  const navigate = useNavigate()
  const { sessionId, setReportInfo } = useFlow()
  const inputRef = useRef(null)

  const [file, setFile] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const [busy, setBusy] = useState(false)
  const [uploadMessage, setUploadMessage] = useState(null)
  const [isError, setIsError] = useState(false)
  const [report, setReport] = useState(null)

  function acceptFile(f) {
    if (!f) return
    const name = f.name.toLowerCase()
    if (!ACCEPTED_EXTENSIONS.some((ext) => name.endsWith(ext))) {
      setUploadMessage('Unsupported file type. Please choose a PDF or an image (PNG/JPG/WEBP).')
      setIsError(true)
      return
    }
    setFile(f)
    setUploadMessage(null)
    setIsError(false)
  }

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
          ? `Report uploaded. ${findingCount > 0 ? `${findingCount} value${findingCount !== 1 ? 's' : ''} extracted.` : 'No structured values found.'}`
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
    <div className="fade-in">
      <Stepper current={3} />

      <div className="card">
        <h2>Medical report (optional)</h2>
        <p style={{ color: 'var(--text-2)' }}>
          Upload a lab report PDF and HealthGuard will extract structured values with their units
          and reference ranges. Nothing is invented — if text cannot be read, you will be told
          clearly.
        </p>

        <div className="alert alert-info">
          <strong>Demo tip:</strong> No lab report at hand? The repository includes a clearly
          labeled synthetic sample report at <code>docs/sample-report.pdf</code> whose values
          this parser reads reliably.
        </div>

        {uploadMessage && (
          <div className={isError ? 'alert alert-warn' : 'alert alert-ok'} role={isError ? 'alert' : 'status'}>
            {uploadMessage}
          </div>
        )}

        {busy && <Loader title="Reading your report" message="Extracting values, units, and reference ranges…" />}

        {!busy && !report && (
          <>
            {!file ? (
              <div
                className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
                role="button"
                tabIndex={0}
                aria-label="Upload a medical report. Drag and drop a PDF or image, or press Enter to choose a file."
                onClick={() => inputRef.current?.click()}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault()
                    inputRef.current?.click()
                  }
                }}
                onDragOver={(e) => {
                  e.preventDefault()
                  setDragOver(true)
                }}
                onDragLeave={() => setDragOver(false)}
                onDrop={(e) => {
                  e.preventDefault()
                  setDragOver(false)
                  acceptFile(e.dataTransfer.files?.[0])
                }}
              >
                <div className="upload-icon" aria-hidden="true">📄</div>
                <div className="upload-title">Upload your medical report</div>
                <div className="upload-hint">Drag &amp; drop, or choose a PDF or image (max 10 MB)</div>
                <button type="button" className="btn btn-secondary" onClick={(e) => { e.stopPropagation(); inputRef.current?.click() }}>
                  Choose file
                </button>
              </div>
            ) : (
              <div className="file-pill">
                <span className="file-icon" aria-hidden="true">
                  {file.name.toLowerCase().endsWith('.pdf') ? '📄' : '🖼️'}
                </span>
                <span>
                  <span className="file-name">{file.name}</span>{' '}
                  <span className="file-size">({formatSize(file.size)})</span>
                </span>
                <button
                  type="button"
                  className="file-remove"
                  aria-label="Remove selected file"
                  onClick={() => setFile(null)}
                >
                  ✕
                </button>
              </div>
            )}

            <input
              ref={inputRef}
              id="file"
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.webp,application/pdf,image/png,image/jpeg,image/webp"
              onChange={(e) => acceptFile(e.target.files?.[0] ?? null)}
              hidden
            />

            <div className="btn-row">
              <button
                type="button"
                className="btn btn-secondary"
                aria-label="Go back to previous step"
                onClick={() => navigate('/follow-up')}
              >
                ← Back
              </button>
              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              <button className="btn btn-secondary" onClick={() => navigate('/analyze')}>
                Skip — I don&apos;t have a report
              </button>
              <button
                className="btn btn-primary"
                disabled={!file}
                onClick={handleUpload}
              >
                {file ? 'Upload & read report' : 'Select a file first'}
              </button>
              </div>
            </div>
          </>
        )}
      </div>

      {report && (
        <div className="card">
          <div className="section-label">Report findings</div>
          <ReportFindings report={report} />
          <div className="btn-row">
            <button
              className="btn btn-secondary"
              onClick={() => {
                setReport(null)
                setFile(null)
                setUploadMessage(null)
              }}
            >
              Upload a different report
            </button>
          </div>
        </div>
      )}

      <div className="btn-row" style={{ marginBottom: 24 }}>
        <button
          type="button"
          className="btn btn-secondary"
          aria-label="Go back to previous step"
          onClick={() => navigate('/follow-up')}
        >
          ← Back
        </button>
        <button
          className="btn btn-primary"
          onClick={() => navigate('/analyze')}
          disabled={busy}
        >
          Continue → Analysis
        </button>
      </div>
    </div>
  )
}
