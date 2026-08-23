import React, { useEffect, useState } from 'react'
import { BadgeCheck, PenLine } from 'lucide-react'
import apiClient from '../api/config'
import Loader from '../components/Loader'

export default function CVWriter() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [data, setData] = useState(null)

  const load = () => {
    setLoading(true)
    setError('')
    apiClient
      .get('/api/ai/writer')
      .then((res) => setData(res.data))
      .catch((err) => setError(err.response?.data?.detail || 'CV Writer needs an analyzed CV first.'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <div className="page-shell">
      <div className="section-head narrow">
        <div>
          <div className="eyebrow">CV WRITER</div>
          <h1>Professional version</h1>
        </div>
      </div>

      {loading && <Loader variant="ai" title="Preparing CV Writer..." message="Loading your analyzed professional context." />}
      {error && <Loader variant="error" title="CV Writer unavailable" message={error} onRetry={load} />}

      {!loading && !error && (
        <div className="split-panel">
          <div className="panel" style={{ padding: '20px' }}>
            <div className="mini-label">YOUR EVIDENCE</div>
            <div className="evidence-list">
              {(data?.evidence || []).length === 0 ? (
                <p>No CV evidence is available yet.</p>
              ) : data.evidence.map((item) => (
                <div key={item} className="evidence-row">
                  <div className="evidence-main">
                    <span className="bullet-dot" />
                    <strong>{item}</strong>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="panel" style={{ padding: '20px' }}>
            <div className="mini-label">PROFESSIONAL VERSION</div>
            <p style={{ marginTop: 0, lineHeight: 1.8 }}>
              {data?.professional_profile || 'Analyze a CV to generate a grounded professional summary.'}
            </p>
            {data?.confirmed_user_intent && (
              <p>Targeting: {data.confirmed_user_intent}</p>
            )}
            <div className="tag-row">
              {(data?.skills || []).slice(0, 8).map((skill) => (
                <span key={skill} className="tag soft">{skill}</span>
              ))}
            </div>
            <div className="quick-actions" style={{ marginTop: 18 }}>
              <button type="button" className="primary-button"><BadgeCheck size={14} /> Keep this evidence</button>
              <button type="button" className="secondary-button"><PenLine size={14} /> Edit in Chat</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
