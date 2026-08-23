import React, { useEffect, useState } from 'react'
import { ArrowRight, Brain, Compass, TrendingUp } from 'lucide-react'
import apiClient from '../api/config'
import Loader from '../components/Loader'

export default function CareerIntelligence() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = () => {
    setLoading(true)
    setError('')
    apiClient
      .get('/api/ai/career-intelligence')
      .then((res) => setData(res.data))
      .catch((err) => setError(err.response?.data?.detail || 'No live intelligence is available until a CV is analyzed.'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <div className="page-shell">
      <div className="section-head narrow">
        <div>
          <div className="eyebrow">CAREER INTELLIGENCE</div>
          <h1>Where your profile is strongest</h1>
        </div>
      </div>

      {loading && <Loader variant="ai" title="Comparing your profile..." message="Using CV evidence, training notes, and confirmed intent." />}
      {error && <Loader variant="error" title="Career Intelligence unavailable" message={error} onRetry={load} />}

      {!loading && !error && data && (
        <>
          <div className="panel intelligence-hero">
            <div className="signal-row strong">
              <Compass size={16} />
              <span>{data.career_signal}</span>
            </div>
            <p>{data.summary}</p>
            {!data.confirmed_user_intent && (data.ai_interpretation?.career_directions || []).length > 1 && (
              <p>Your CV suggests {(data.ai_interpretation.career_directions || []).join(' and ')}. Confirm which direction you are targeting on the CV page.</p>
            )}
          </div>

          <div className="split-panel">
            <div className="panel">
              <div className="mini-label">STRONG EVIDENCE</div>
              {(data.strong_evidence || []).length === 0 ? (
                <p>No strong evidence is available yet. Add a CV or training update to improve the signal.</p>
              ) : (
                <ul className="check-list">
                  {data.strong_evidence.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              )}
            </div>

            <div className="panel">
              <div className="mini-label">NEXT GAP</div>
              <h3>{data.next_gaps?.[0] || 'Add evidence'}</h3>
              <p>{data.next_gaps?.length ? 'This gap is inferred from your CV analysis, not invented.' : 'No gap is currently identified from your available evidence.'}</p>
              <button type="button" className="text-button">
                Explore learning path <ArrowRight size={14} />
              </button>
            </div>
          </div>

          <div className="panel insight-panel compact">
            <div className="signal-row">
              <TrendingUp size={16} />
              <span>{data.confirmed_user_intent || data.ai_recommendation?.current_intent || 'Confirm your career intent to separate it from CV history.'}</span>
            </div>
            <div className="signal-row muted">
              <Brain size={16} />
              <span>{(data.ai_interpretation?.career_directions || []).join(', ') || 'AVIS will suggest a more specific plan as more evidence is added.'}</span>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
