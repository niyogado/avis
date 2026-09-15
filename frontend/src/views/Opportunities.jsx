import React, { useEffect, useState } from 'react'
import { ArrowRight, BriefcaseBusiness, MapPin } from 'lucide-react'
import apiClient from '../api/config'

export default function Opportunities() {
  const [jobs, setJobs] = useState([])
  const [message, setMessage] = useState('Loading opportunities…')

  useEffect(() => {
    let active = true
    apiClient
      .get('/api/ai/opportunities')
      .then((res) => {
        if (!active) return
        const items = res.data?.jobs || []
        setJobs(items)
        setMessage(res.data?.message || (items.length ? 'Profile-based recommendations are available.' : 'No live opportunities are configured yet.'))
      })
      .catch(() => {
        if (active) {
          setJobs([])
          setMessage('No live opportunity provider is configured for AVIS yet.')
        }
      })

    return () => { active = false }
  }, [])

  return (
    <div className="page-shell">
      <div className="section-head narrow">
        <div>
          <div className="eyebrow">OPPORTUNITIES</div>
          <h1>Relevant next roles</h1>
        </div>
      </div>

      <div className="panel" style={{ padding: '18px 20px', marginBottom: 18 }}>
        <small>{message}</small>
      </div>

      <div className="stack-list">
        {jobs.length === 0 ? (
          <div className="panel" style={{ padding: '24px 20px' }}>No live opportunity list is configured yet. Add a provider to enable role matching.</div>
        ) : jobs.map((job) => (
          <div key={`${job.title}-${job.company}`} className="panel opportunity-item">
            <div className="opportunity-header">
              <div className="title-line">
                <span className="mini-icon"><BriefcaseBusiness size={16} /></span>
                <div>
                  <strong>{job.title}</strong>
                  <small>{job.company}</small>
                </div>
              </div>
              <span className="status-badge">{job.fit}</span>
            </div>

            <div className="meta-row">
              <span><MapPin size={14} /> {job.location}</span>
            </div>

            <div className="tag-row">
              {(job.skills || []).map((skill) => (
                <span key={skill} className="tag soft">{skill}</span>
              ))}
            </div>

            <div className="opportunity-footer">
              <div>
                <small>Gap</small>
                <strong>{job.gap}</strong>
              </div>
              <button type="button" className="text-button">
                View opportunity <ArrowRight size={14} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
