import React, { useEffect, useState } from 'react'
import { Brain, BriefcaseBusiness, Code2, FolderGit2, GraduationCap, Target, TrendingUp } from 'lucide-react'
import apiClient from '../api/config'

export default function Identity() {
  const [profile, setProfile] = useState(null)
  const [intelligence, setIntelligence] = useState(null)

  useEffect(() => {
    let active = true

    Promise.all([
      apiClient.get('/api/profile/').catch(() => null),
      apiClient.get('/api/ai/career-intelligence').catch(() => null),
    ]).then(([profileRes, intelRes]) => {
      if (!active) return
      setProfile(profileRes?.data || null)
      setIntelligence(intelRes?.data || null)
    })

    return () => { active = false }
  }, [])

  const fullName = profile?.full_name || [profile?.first_name, profile?.last_name].filter(Boolean).join(' ') || 'Your profile'
  const role = profile?.headline || intelligence?.career_signal || 'Professional identity'
  const nodes = [
    { label: 'Skills', icon: Code2, active: true, description: (intelligence?.strong_evidence || []).slice(0, 3).join(', ') || 'Awaiting evidence' },
    { label: 'Experience', icon: BriefcaseBusiness, description: role },
    { label: 'Projects', icon: FolderGit2, description: profile?.summary ? 'Profile summary available' : 'No project evidence yet' },
    { label: 'Learning', icon: GraduationCap, description: (intelligence?.next_gaps || []).slice(0, 2).join(', ') || 'No active gaps' },
    { label: 'Goals', icon: Target, description: profile?.location || 'Location not set' },
  ]

  const evidence = (intelligence?.strong_evidence || []).length
    ? intelligence.strong_evidence.map((item) => ({ title: item, source: 'Verified signal', tone: 'Strong evidence' }))
    : [{ title: 'No evidence yet', source: 'Profile', tone: 'Waiting' }]

  return (
    <div className="page-shell identity-page">
      <div className="section-head">
        <div>
          <div className="eyebrow">IDENTITY</div>
          <h1>{fullName}</h1>
        </div>
        <div className="identity-role">
          <span>{role}</span>
          <small>{profile?.location || 'Location not set'}</small>
        </div>
      </div>

      <div className="identity-map panel">
        <div className="identity-line" />
        <div className="identity-grid">
          {nodes.map(({ label, icon: Icon, description, active }) => (
            <button type="button" key={label} className={`identity-node ${active ? 'active' : ''}`}>
              <span className="node-icon"><Icon size={16} /></span>
              <span>{label}</span>
              <small>{description}</small>
            </button>
          ))}
        </div>
      </div>

      <div className="split-panel">
        <div className="panel evidence-panel">
          <div className="mini-label">EVIDENCE</div>
          <div className="evidence-list">
            {evidence.map((item) => (
              <div key={item.title} className="evidence-row">
                <div className="evidence-main">
                  <span className="bullet-dot" />
                  <div>
                    <strong>{item.title}</strong>
                    <small>{item.source}</small>
                  </div>
                </div>
                <span className={`tag ${item.tone === 'Gap to close' ? 'warning' : ''}`}>{item.tone}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="panel insight-panel">
          <div className="mini-label">CURRENT SIGNAL</div>
          <h3>Strongest identity cluster</h3>
          <p>{intelligence?.summary || 'Add a profile or CV to establish a stronger identity signal.'}</p>
          <div className="signal-row">
            <TrendingUp size={16} />
            <span>Career signal: {intelligence?.career_signal || 'Not yet determined'}</span>
          </div>
          <div className="signal-row muted">
            <Brain size={16} />
            <span>Next strategic gap: {(intelligence?.next_gaps || [])[0] || 'Add evidence to identify a gap'}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
