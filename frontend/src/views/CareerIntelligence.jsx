import React, { useEffect, useState } from 'react'
import { Brain, Compass, CheckCircle, Target, BookOpen, ExternalLink } from 'lucide-react'
import { Link } from 'react-router-dom'
import apiClient from '../api/config'
import Loader from '../components/Loader'

function pathStrength(path) {
  const source = path.source
  if (source === 'user_confirmed') return { label: 'Confirmed', color: 'amber', icon: CheckCircle }
  if (source === 'cv_supported') return { label: 'CV supported', color: 'blue', icon: Target }
  return { label: 'AI possible', color: 'slate', icon: Brain }
}

export default function CareerIntelligence() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedPath, setSelectedPath] = useState(null)

  const load = () => {
    setLoading(true)
    setError('')
    apiClient
      .get('/api/ai/career-intelligence')
      .then((res) => {
        setData(res.data)
        const paths = res.data?.career_paths || []
        const confirmed = paths.find((p) => p.source === 'user_confirmed')
        setSelectedPath(confirmed || paths[0] || null)
      })
      .catch((err) => setError(err.response?.data?.detail || 'No live intelligence is available until a CV is analyzed.'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  if (loading) return <Loader variant="ai" title="Comparing your profile..." message="Using CV evidence, training notes, and confirmed intent." />
  if (error) return <Loader variant="error" title="Career Intelligence unavailable" message={error} onRetry={load} />
  if (!data) return null

  const paths = data.career_paths || []
  const active = selectedPath || paths[0]

  return (
    <div className="page-shell">
      <div className="section-head narrow">
        <div>
          <div className="eyebrow">CAREER INTELLIGENCE</div>
          <h1>Where your profile is strongest</h1>
        </div>
      </div>

      <div className="panel intelligence-hero">
        <div className="signal-row strong">
          <Compass size={16} />
          <span>{data.career_signal}</span>
        </div>
        <p>{data.summary}</p>
      </div>

      {!data.confirmed_user_intent &&
        (data.ai_interpretation?.career_directions || []).length > 1 && (
          <p className="hint">
            Your CV suggests {(data.ai_interpretation.career_directions || []).join(' and ')}.
            Confirm which direction you are targeting on the CV page.
          </p>
        )}

      {paths.length > 0 && (
        <div className="panel">
          <div className="mini-label">CAREER DIRECTIONS</div>
          <div className="path-tabs">
            {paths.map((p) => {
              const meta = pathStrength(p)
              const Icon = meta.icon
              const selected = active && active.label === p.label
              return (
                <button
                  key={p.label}
                  type="button"
                  className={`path-tab ${selected ? 'selected' : ''} ${meta.color}`}
                  onClick={() => setSelectedPath(p)}
                >
                  <Icon size={14} />
                  <span>{p.label}</span>
                  <span className="path-badge" title={meta.label}>{meta.label}</span>
                </button>
              )
            })}
          </div>
        </div>
      )}
                  {error && <Loader variant="error" title="Career Intelligence unavailable" message={error} onRetry={load} />}

      {/* Per-direction intelligence: strengths / gaps / recommendations */}
      {active && (
        <div className="split-panel">
          <div className="panel">
            <div className="mini-label">STRENGTHS FOR {(active.label || 'this direction').toUpperCase()}</div>
            {(active.strengths || []).length === 0 ? (
              <p className="hint">No direct evidence overlap yet for this direction.</p>
            ) : (
              <ul className="check-list">
                {(active.strengths || []).map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ul>
            )}
          </div>

          <div className="panel">
            <div className="mini-label">NEXT GAP</div>
            <h3>{(active.gaps || [])[0] || 'Add evidence'}</h3>
            <p>
              {(active.gaps || []).length
                ? 'This gap is inferred from your CV analysis, not invented.'
                : 'No specific gap is identified for this direction yet.'}
            </p>
            {(active.recommended_skills || []).length > 0 && (
              <div className="tag-list">
                {(active.recommended_skills || []).slice(0, 8).map((s) => (
                  <span key={s} className="skill-tag">{s}</span>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Recommendations for this direction */}
      {active && (active.recommendations || []).length > 0 && (
        <div className="panel">
          <div className="mini-label">RECOMMENDATIONS FOR {(active.label || 'this direction').toUpperCase()}</div>
          <ul className="check-list">
            {(active.recommendations || []).map((rec, i) => (
              <li key={`rec-${i}`}>{rec}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Why this direction? */}
      {active && active.why && (
        <div className="panel insight-panel compact">
          <div className="signal-row">
            <Brain size={16} />
            <span>Why this direction?</span>
          </div>
          <ul className="check-list">
            {(active.why || []).map((w, i) => (
              <li key={`why-${i}`}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Quick jump to Learning / Opportunities */}
      <div className="panel">
        <div className="mini-label">CONTINUE</div>
        <div className="action-links">
          <Link to="/career" className="text-button">
            See opportunities for this direction <ExternalLink size={14} />
          </Link>
          <Link to="/learning" className="text-button">
            View the learning path <BookOpen size={14} />
                    </Link>
        </div>
      </div>
    </div>
  )
}
