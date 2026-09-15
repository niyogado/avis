import React from 'react'
import { Bell } from 'lucide-react'

export default function JobAlerts() {
  return (
    <div className="page-shell">
      <div className="section-head narrow">
        <div>
          <div className="eyebrow">JOB ALERTS</div>
          <h1>Your career signal</h1>
        </div>
      </div>

      <div className="stack-list">
        <div className="panel" style={{ padding: '18px 20px' }}>
          <div className="opportunity-header">
            <div className="title-line">
              <span className="mini-icon"><Bell size={16} /></span>
              <div>
                <strong>No active alerts</strong>
                <small>No live job source is configured</small>
              </div>
            </div>
            <span className="status-badge">Disabled</span>
          </div>
        </div>
      </div>
    </div>
  )
}
