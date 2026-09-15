import React from 'react'
import { useAuth } from '../contexts/AuthContext'

export default function Settings() {
  const { user, token } = useAuth()

  const settings = [
    { label: 'AI recommendations', value: 'Enabled' },
    { label: 'Profile visibility', value: 'Private' },
    { label: 'Notifications', value: 'Daily digest' },
    { label: 'Theme', value: 'Light mode' },
    { label: 'Account', value: user?.email || 'Not signed in' },
    { label: 'Authentication', value: token ? 'Authenticated' : 'Logged out' },
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
