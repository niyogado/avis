import React from 'react'
import { useAuth } from '../contexts/AuthContext'

export default function Settings() {
  const { user, token } = useAuth()

  const settings = [
    { label: 'Account', value: user?.email || user?.full_name || 'Not signed in' },
    { label: 'Authentication', value: token ? 'Authenticated' : 'Logged out' },
    { label: 'AI recommendations', value: 'Uses your CV, training notes, and confirmed intent' },
    { label: 'Job search provider', value: 'Not configured' },
    { label: 'Notification preferences', value: 'Not configurable yet' },
    { label: 'Theme', value: 'Uses the current AVIS professional theme' },
  ]

  return (
    <div className="page-shell">
      <div className="section-head narrow">
        <div>
          <div className="eyebrow">SETTINGS</div>
          <h1>Professional preferences</h1>
        </div>
      </div>

      <div className="panel" style={{ padding: '20px' }}>
        {settings.map((item) => (
          <div key={item.label} className="list-row">
            <strong>{item.label}</strong>
            <span>{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
