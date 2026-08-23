import React, { useEffect, useState } from 'react'
import { ArrowUpRight, Bell, BriefcaseBusiness, Compass, Send } from 'lucide-react'
import apiClient from '../api/config'
import Loader from '../components/Loader'

const TABS = [
  { id: 'opportunities', label: 'Opportunities' },
  { id: 'applications', label: 'Applications' },
  { id: 'alerts', label: 'Job Alerts' },
]

const isValidApplyUrl = (value) => {
  if (typeof value !== 'string') return false
  return /^https?:\/\//i.test(value.trim())
}

const anchorStyle = {
  textDecoration: 'none',
  display: 'inline-flex',
  alignItems: 'center',
  gap: 6,
}

const headingFor = (tab) => {
  if (tab === 'applications') return 'Applications I chose to pursue'
  if (tab === 'alerts') return 'Alerts based on confirmed career preferences'
  return 'AI-recommended opportunities'
}

function JobCard({ job, saving, saved, onSave }) {
  const applyUrl = job.application_url || job.url
  const matchLabel = job.match_score != null ? `Match: ${job.match_score}%` : (job.match_band || 'Potential match')
  return (
    <div className="panel opportunity-item">
      <div className="opportunity-header">
        <div className="title-line">
          {job.company_logo ? (
            <img
              src={job.company_logo}
              alt=""
              width={28}
              height={28}
              style={{ borderRadius: 8, border: '1px solid var(--border)', objectFit: 'cover' }}
            />
          ) : (
            <span className="mini-icon"><BriefcaseBusiness size={16} /></span>
          )}
          <div>
            <strong>{job.title}</strong>
            <small>
              {[job.company || 'Organization not specified', job.location || 'Location not stated', job.employment_type || job.sector]
                .filter(Boolean).join(' • ')}
            </small>
          </div>
        </div>
        <span className={`status-badge ${job.match_score != null ? '' : 'soft'}`}>{matchLabel}</span>
      </div>

      {job.ai_match_insight && (
        <div style={{ marginTop: 12 }}>
          <div className="mini-label">AI MATCH INSIGHTS</div>
          <p style={{ margin: '6px 0 0', fontStyle: 'italic', lineHeight: 1.6 }}>
            “{job.ai_match_insight}”
          </p>
        </div>
      )}

      {job.description_snippet && (
        <div style={{ marginTop: 12 }}>
          <div className="mini-label">DESCRIPTION SNIPPET</div>
          <p style={{ margin: '6px 0 0', lineHeight: 1.6, color: 'var(--text-soft)' }}>
            {job.description_snippet}
          </p>
        </div>
      )}

      {(job.match_reasons || []).length > 0 && (
        <div className="tag-row" style={{ marginTop: 12 }}>
          {job.match_reasons.slice(0, 4).map((reason) => (
            <span key={reason} className="tag soft">{reason}</span>
          ))}
        </div>
      )}

      <div className="opportunity-footer">
        <div>
          <small>Found on {job.source} · application link verified</small>
          <strong>{job.salary || 'Salary not disclosed'}</strong>
        </div>
        <div className="quick-actions" style={{ marginTop: 0 }}>
          <button type="button" className="secondary-button" onClick={onSave} disabled={saving || saved}>
            <Send size={13} /> {saved ? 'Saved' : 'Save'}
          </button>
          <a href={applyUrl} target="_blank" rel="noopener noreferrer" className="primary-button" style={anchorStyle}>
            Apply Now <ArrowUpRight size={14} />
          </a>
        </div>
      </div>
    </div>
  )
}
export default function CareerHub() {
  const [activeTab, setActiveTab] = useState('opportunities')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [jobs, setJobs] = useState([])
  const [routing, setRouting] = useState(null)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(false)
  const [loadingMore, setLoadingMore] = useState(false)
  const [applications, setApplications] = useState([])
  const [alerts, setAlerts] = useState([])
  const [alertDraft, setAlertDraft] = useState('')
  const [saving, setSaving] = useState(false)
  const [savedIds, setSavedIds] = useState([])
  const [context, setContext] = useState({ confirmed_user_intent: '', skills: [], target_roles: [] })

  const applyOps = (ops, { append }) => {
    const incoming = ops.data?.jobs || []
    setJobs((current) => {
      if (!append) return incoming
      const seen = new Set(current.map((job) => job.application_url || job.url))
      const fresh = incoming.filter((job) => !seen.has(job.application_url || job.url))
      return [...current, ...fresh]
    })
    setRouting(ops.data?.routing || null)
    setMessage(ops.data?.message || '')
    setContext(ops.data?.context || { confirmed_user_intent: '', skills: [], target_roles: [] })
    setPage(ops.data?.page || 1)
    setHasMore(Boolean(ops.data?.has_more) && incoming.length > 0)
  }

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const [ops, apps, alertRes] = await Promise.all([
        apiClient.get('/api/ai/opportunities?page=1'),
        apiClient.get('/api/ai/applications'),
        apiClient.get('/api/ai/job-alerts'),
      ])
      applyOps(ops, { append: false })
      const items = apps.data?.items || []
      setApplications(items)
      setSavedIds(items.map((item) => item.source_url).filter(Boolean))
      setAlerts(alertRes.data?.items || [])
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to load Career Hub.')
    } finally {
      setLoading(false)
    }
  }

  const exploreMore = async () => {
    if (loadingMore || !hasMore) return
    setLoadingMore(true)
    setError('')
    try {
      const next = page + 1
      const ops = await apiClient.get(`/api/ai/opportunities?page=${next}`)
      applyOps(ops, { append: true })
      if (!(ops.data?.jobs || []).length) {
        setMessage('No further verified opportunities were found for this exploration batch.')
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to load more opportunities.')
    } finally {
      setLoadingMore(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const createAlert = async () => {
    if (!alertDraft.trim() || saving) return
    setSaving(true)
    try {
      await apiClient.post('/api/ai/job-alerts', {
        title: alertDraft.trim(),
        query: alertDraft.trim(),
        target_roles: context.confirmed_user_intent ? [context.confirmed_user_intent] : [],
      })
      setAlertDraft('')
      await load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to save this alert.')
    } finally {
      setSaving(false)
    }
  }

  const saveJob = async (job) => {
    if (saving) return
    setSaving(true)
    try {
      await apiClient.post('/api/ai/applications', {
        title: job.title,
        company: job.company,
        location: job.location,
        source_url: job.source_url,
        match_score: job.match_score,
        match_reasons: job.match_reasons || [],
        notes: 'Saved by user from Career Hub. External submission was not performed.',
      })
      await load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to save this application.')
    } finally {
      setSaving(false)
    }
  }

  // Client-edge strict validation: never render a card without a real direct
  // application URL, even if a provider slips an invalid one through.
  const renderableJobs = jobs.filter((job) => isValidApplyUrl(job.application_url) || isValidApplyUrl(job.url))
  const intent = context.confirmed_user_intent || (context.target_roles || []).join(', ')

  return (
    <div className="page-shell">
<div className="section-head narrow">
        <div>
          <div className="eyebrow">CAREER HUB</div>
          <h1>{headingFor(activeTab)}</h1>
        </div>
      </div>

      <div className="cv-preview-toolbar" style={{ marginBottom: 18 }}>
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={activeTab === tab.id ? 'inline-button active' : 'inline-button'}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {loading && <Loader variant="fetch" title="Loading Career Hub..." message="Fetching opportunities, applications, and alerts." />}
      {error && <Loader variant="error" title="Career Hub unavailable" message={error} onRetry={load} />}

      {!loading && !error && activeTab === 'opportunities' && (
        <>
          <div className="panel" style={{ padding: '18px 20px', marginBottom: 18 }}>
            <div className="signal-row">
              <Compass size={16} />
              <span>{message}</span>
            </div>
            {intent && <p style={{ marginBottom: 0 }}>Confirmed direction: {intent}</p>}
          </div>

          <div className="mini-label" style={{ marginTop: 18 }}>VERIFIED OPPORTUNITIES FOR YOUR FIELD</div>
          {renderableJobs.length === 0 ? (
            <div className="stack-list">
              <div className="panel" style={{ padding: '24px 20px' }}>
                No verified opportunities are available for your field right now. Only listings with a real application link are shown — AVIS never displays empty or placeholder cards.
              </div>
            </div>
          ) : (
            <>
              <div className="stack-list">
                {renderableJobs.map((job) => (
                  <JobCard
                    key={`${job.application_url || job.url}-${job.company || ''}`}
                    job={job}
                    saving={saving}
                    saved={savedIds.includes(job.source_url)}
                    onSave={() => saveJob(job)}
                  />
                ))}
              </div>
              {hasMore && (
                <div style={{ display: 'flex', justifyContent: 'center', marginTop: 6 }}>
                  <button type="button" className="secondary-button" onClick={exploreMore} disabled={loadingMore}>
                    {loadingMore ? 'Exploring more roles…' : 'Explore More Opportunities'}
                  </button>
                </div>
              )}
            </>
          )}
        </>
      )}
      {!loading && !error && activeTab === 'applications' && (
        <div className="stack-list">
          {applications.length === 0 ? (
            <div className="panel" style={{ padding: '24px 20px' }}>
              No applications yet. AVIS can recommend roles, but only you can choose to pursue one.
            </div>
          ) : applications.map((item) => (
            <div key={item.id} className="panel" style={{ padding: '18px 20px' }}>
              <div className="opportunity-header">
                <div className="title-line">
                  <span className="mini-icon"><Send size={16} /></span>
                  <div>
                    <strong>{item.title}</strong>
                    <small>{item.company || 'Company not specified'}</small>
                  </div>
                </div>
                <span className="status-badge">{item.status}</span>
              </div>
              <p>{item.notes || 'Saved by you. No external application was submitted automatically.'}</p>
            </div>
          ))}
        </div>
      )}

      {!loading && !error && activeTab === 'alerts' && (
        <div className="stack-list">
          <div className="panel" style={{ padding: '18px 20px' }}>
            <div className="mini-label">CREATE ALERT</div>
            <p>Alerts capture your confirmed career preferences. When a live provider connection is added, matching opportunities can appear here automatically.</p>
            <div className="quick-actions" style={{ marginTop: 14 }}>
              <input
                value={alertDraft}
                onChange={(event) => setAlertDraft(event.target.value)}
                placeholder={context.confirmed_user_intent || 'Role or keyword to watch'}
                style={{ flex: 1, borderRadius: 12, border: '1px solid var(--border)', padding: '10px 12px', background: 'rgba(255,255,255,0.4)', color: 'var(--text)' }}
              />
              <button type="button" className="primary-button" onClick={createAlert} disabled={saving || !alertDraft.trim()}>
                Save alert
              </button>
            </div>
          </div>
          {alerts.length === 0 ? (
            <div className="panel" style={{ padding: '18px 20px' }}>
              <div className="title-line">
                <span className="mini-icon"><Bell size={16} /></span>
                <div>
                  <strong>No active alerts</strong>
                  <small>Create one from your confirmed direction</small>
                </div>
              </div>
            </div>
          ) : alerts.map((item) => (
            <div key={item.id} className="panel" style={{ padding: '18px 20px' }}>
              <div className="opportunity-header">
                <div className="title-line">
                  <span className="mini-icon"><Bell size={16} /></span>
                  <div>
                    <strong>{item.title}</strong>
                    <small>{item.query}</small>
                  </div>
                </div>
                <span className="status-badge">{item.is_active ? 'Active' : 'Paused'}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
