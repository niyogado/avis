import React, { useEffect, useState } from 'react'
import { ArrowRight, Brain, BriefcaseBusiness } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import apiClient from '../api/config'
import Loader from '../components/Loader'

export default function Overview() {
  const { user } = useAuth()
  const [intelligence, setIntelligence] = useState(null)
  const [cv, setCv] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = () => {
    setLoading(true)
    setError('')
    Promise.all([
      apiClient.get('/api/ai/career-intelligence').catch(() => null),
      apiClient.get('/api/cv/').catch(() => null),
    ]).then(([intelRes, cvRes]) => {
      setIntelligence(intelRes?.data || null)
      setCv((cvRes?.data || [])[0] || null)
      if (!intelRes && !cvRes) setError('Unable to load your AVIS overview.')
    }).finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  const firstName = user?.full_name?.split(' ')[0] || user?.first_name || 'there'
  const insight = intelligence
  const cvStatus = cv?.analysis_status === 'success' ? 'Analyzed' : cv ? 'Uploaded' : 'Missing'

  return (
    <div className="page-shell">
      <div className="section-head">
        <div>
          <div className="eyebrow">TODAY</div>
          <h1>Good evening, {firstName}.</h1>
        </div>
      </div>

      {loading && <Loader variant="fetch" title="Loading overview..." message="Reading your CV status and career context." />}
      {error && <Loader variant="error" title="Overview unavailable" message={error} onRetry={load} />}

      {!loading && (
        <>
          <div className="overview-grid">
            <div className="panel metric-panel">
              <div className="label">CV</div>
              <div className="value">{cvStatus}</div>
            </div>
            <div className="panel metric-panel">
              <div className="label">Career direction</div>
              <div className="value">{insight?.confirmed_user_intent || insight?.career_signal || 'Not confirmed'}</div>
            </div>
            <div className="panel metric-panel">
              <div className="label">Evidence items</div>
              <div className="value">{String(insight?.strong_evidence?.length || 0)}</div>
            </div>
            <div className="panel metric-panel">
              <div className="label">Gaps</div>
              <div className="value">{String(insight?.next_gaps?.length || 0)}</div>
            </div>
          </div>

          <div className="panel hero-panel">
            <div className="hero-copy">
              <div className="greeting">
                {insight?.summary || 'Upload and analyze a CV to give AVIS a professional starting point.'}
              </div>
              <div className="quick-actions">
                <Link to="/cv" className="primary-button">Review CV</Link>
                <Link to="/career/intelligence" className="secondary-button">Career Intelligence</Link>
              </div>
            </div>
            <div className="feature-block">
              <div className="label">NEXT BEST ACTION</div>
              <div>
                <strong>{insight?.next_gaps?.[0] || (cv ? 'Confirm your career intent' : 'Upload a CV')}</strong>
                <p>{cv?.filename || 'No CV is stored yet.'}</p>
              </div>
              <Link to={cv ? '/training' : '/cv'} className="text-button">
                Continue <ArrowRight size={14} />
              </Link>
              <div className="detail"><BriefcaseBusiness size={14} /> {insight?.strong_evidence?.length || 0} evidence items currently available.</div>
            </div>
          </div>

          <div className="split-panel">
            <div className="panel">
              <div className="mini-label">FOCUS</div>
              <div className="list-row">
                <div>
                  <strong>CV memory</strong>
                  <div>{cv ? `${cv.filename} is ${cvStatus.toLowerCase()}.` : 'AVIS does not have a CV yet.'}</div>
                </div>
                <Link to="/cv" className="text-button small">Open <ArrowRight size={12} /></Link>
              </div>
              <div className="list-row">
                <div>
                  <strong>Career Hub</strong>
                  <div>Opportunities, applications, and alerts live in one workspace.</div>
                </div>
                <Link to="/career" className="text-button small">Open <ArrowRight size={12} /></Link>
              </div>
            </div>
            <div className="panel">
              <div className="mini-label">CAREER SIGNAL</div>
              <div className="list-row">
                <div>
                  <strong>{insight?.career_signal || 'Not yet determined'}</strong>
                  <small>{insight?.confirmed_user_intent ? 'User-confirmed intent' : 'AI inference until you confirm'}</small>
                </div>
                <span className="status-badge">{insight ? 'Live' : 'Waiting'}</span>
              </div>
              {(insight?.next_gaps || []).slice(0, 2).map((gap) => (
                <div key={gap} className="list-row">
                  <div>
                    <strong>{gap}</strong>
                    <small>Current gap</small>
                  </div>
                  <span className="tag warning">Needs evidence</span>
                </div>
              ))}
              <div className="list-row">
                <div>
                  <strong>AI context</strong>
                  <small><Brain size={12} /> Chat uses this same professional memory.</small>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
