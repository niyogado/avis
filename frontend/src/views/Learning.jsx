import React, { useEffect, useState } from 'react'
import { ArrowRight, BookOpen, CheckCircle2 } from 'lucide-react'
import apiClient from '../api/config'
import Loader from '../components/Loader'

export default function Learning() {
  const [lessons, setLessons] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = () => {
    setLoading(true)
    setError('')
    apiClient
      .get('/api/ai/career-intelligence')
      .then((res) => {
        const gaps = res.data?.next_gaps || []
        setLessons(gaps.map((gap) => ({
          title: gap,
          reason: `Inferred from your ${res.data?.confirmed_user_intent || res.data?.career_signal || 'current career context'}.`,
        })))
      })
      .catch((err) => setError(err.response?.data?.detail || 'Upload a CV before AVIS can recommend learning from real gaps.'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <div className="page-shell">
      <div className="section-head narrow">
        <div>
          <div className="eyebrow">LEARNING</div>
          <h1>Recommended next</h1>
        </div>
      </div>

      {loading && <Loader variant="ai" title="Comparing your profile..." message="Reading inferred skill gaps from your CV analysis." />}
      {error && <Loader variant="error" title="Learning unavailable" message={error} onRetry={load} />}

      {!loading && !error && (
        <div className="stack-list">
          {lessons.length === 0 ? (
            <div className="panel" style={{ padding: '20px' }}>No inferred gaps yet. Analyze a CV to populate this list from real evidence.</div>
          ) : lessons.map((lesson) => (
            <div key={lesson.title} className="panel learning-item">
              <div className="learning-top">
                <span className="mini-icon"><BookOpen size={16} /></span>
                <div>
                  <h3>{lesson.title}</h3>
                  <p>{lesson.reason}</p>
                </div>
              </div>
              <div className="learning-meta">
                <span className="status-badge soft"><CheckCircle2 size={12} /> From CV analysis</span>
              </div>
              <button type="button" className="text-button">
                Explore <ArrowRight size={14} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
