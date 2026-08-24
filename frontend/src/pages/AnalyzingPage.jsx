import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Stepper from '../components/Stepper.jsx'
import Loader from '../components/Loader.jsx'
import { api } from '../services/api.js'
import { useFlow } from '../context/FlowContext.jsx'

export default function AnalyzingPage() {
  const navigate = useNavigate()
  const { sessionId, setLastAnalysisId } = useFlow()
  const [error, setError] = useState(null)
  const attempted = useRef(false)

  useEffect(() => {
    if (!sessionId) {
      navigate('/profile')
      return
    }
    if (attempted.current) return
    attempted.current = true

    api
      .analyze(sessionId)
      .then((analysis) => {
        setLastAnalysisId(analysis.id)
        navigate(`/results/${analysis.id}`)
      })
      .catch((err) => setError(err.message))
  }, [sessionId, navigate, setLastAnalysisId])

  return (
    <div>
      <Stepper current={4} />
      <div className="card">
        {error ? (
          <div style={{ textAlign: 'center', padding: '30px 10px' }}>
            <h2>Analysis could not be completed</h2>
            <div className="error-box">{error}</div>
            <button className="btn btn-secondary" onClick={() => window.location.reload()}>
              Try again
            </button>
          </div>
        ) : (
          <Loader
            message="Combining your profile, symptoms, answers, and report into a preliminary assessment…"
          />
        )}
      </div>
    </div>
  )
}
