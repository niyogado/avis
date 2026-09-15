import React, { useEffect, useState } from 'react'
import { ArrowRight, Brain, BriefcaseBusiness } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import apiClient from '../api/config'

export default function Overview() {
  const { user } = useAuth()
  const [intelligence, setIntelligence] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    apiClient
      .get('/api/ai/career-intelligence')
      .then((res) => {
        if (active) setIntelligence(res.data)
      })
      .catch(() => {
        if (active) setIntelligence(null)
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  const firstName = user?.full_name?.split(' ')[0] || user?.first_name || 'there'
  const insight = intelligence || {
    career_signal: 'Professional identity',
    strong_evidence: ['Profile data', 'Training notes'],
    next_gaps: ['Add more verified evidence'],
    summary: 'More evidence is needed before AVIS can rank your top opportunities with confidence.',
  }

  const metrics = [
    { label: 'Career signal', value: insight.career_signal || 'N/A' },
    { label: 'Strong evidence', value: String(insight.strong_evidence?.length || 0) },
    { label: 'Next gaps', value: String(insight.next_gaps?.length || 0) },
    { label: 'Status', value: loading ? 'Loading' : 'Live' },
  ]

  const actions = [
    { title: 'Add stronger evidence', detail: 'Capture a recent project, achievement, or training update so AVIS can refine your signal.' },
    { title: 'Review your strongest path', detail: `The current strongest direction is ${insight.career_signal}.` },
  ]

  return (
    <div className="page-shell">
      <div className="section-head">
        <div>
          <div className="eyebrow">TODAY</div>
          <h1>Good evening, {firstName}.</h1>
        </div>
      </div>

      <div className="overview-grid">
        {metrics.map((item) => (
          <div key={item.label} className="panel metric-panel">
            <div className="label">{item.label}</div>
            <div className="value">{item.value}</div>
          </div>
        ))}
      </div>

      <div className="panel hero-panel">
        <div className="hero-copy">
          <div className="greeting">
            Your professional identity is evolving.
            <strong>{insight.career_signal || 'More evidence is needed'} is the current signal.</strong>
          </div>

          <div className="meta-copy">
            {insight.summary || 'AVIS is consolidating your CV, training, and approved knowledge into a coherent professional identity.'}
          </div>

          <div className="quick-actions">
            <button type="button" className="primary-button">Review</button>
            <button type="button" className="secondary-button">Improve evidence</button>
          </div>
        </div>

        <div className="feature-block">
          <div className="label">NEXT BEST ACTION</div>
          <div>
            <strong>{insight.next_gaps?.[0] || 'Capture a recent achievement'}</strong>
            <p>{insight.summary || 'Add more verified evidence to sharpen the AI signal.'}</p>
          </div>

          <button type="button" className="text-button">
            Improve evidence <ArrowRight size={14} />
          </button>

          <div className="detail"><BriefcaseBusiness size={14} /> {insight.strong_evidence?.length || 0} evidence categories are currently visible.</div>
        </div>
      </div>

      <div className="split-panel">
        <div className="panel">
          <div className="mini-label">FOCUS</div>
          {actions.map((action) => (
            <div key={action.title} className="list-row">
              <div>
                <strong>{action.title}</strong>
                <div>{action.detail}</div>
              </div>
              <button type="button" className="text-button small">
                Review <ArrowRight size={12} />
              </button>
            </div>
          ))}
        </div>

        <div className="panel">
          <div className="mini-label">CAREER SIGNAL</div>
          <div className="list-row">
            <div>
              <strong>{insight.career_signal}</strong>
              <small>Strongest aligned path</small>
            </div>
            <span className="status-badge">Live</span>
          </div>
          {(insight.next_gaps || []).slice(0, 2).map((gap) => (
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
              <strong>Profile quality</strong>
              <small>Grounded in verified data</small>
            </div>
            <span className="tag soft">Updated</span>
          </div>
        </div>
      </div>
    </div>
  )
}