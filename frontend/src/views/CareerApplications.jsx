import React from 'react'
import { ArrowRight, Send } from 'lucide-react'

export default function CareerApplications() {
  return (
    <div className="page-shell">
      <div className="section-head narrow">
        <div>
          <div className="eyebrow">APPLICATIONS</div>
          <h1>Minimal application tracker</h1>
        </div>
      </div>

      <div className="panel" style={{ padding: '24px 20px' }}>
        No application workflow is connected yet. Add an ATS or CRM integration to track real applications here.
      </div>

      <div className="stack-list">
        <div className="panel" style={{ padding: '18px 20px' }}>
          <div className="opportunity-header">
            <div className="title-line">
              <span className="mini-icon"><Send size={16} /></span>
              <div>
                <strong>No live applications</strong>
                <small>Awaiting integration</small>
              </div>
            </div>
            <span className="status-badge">Waiting</span>
          </div>
          <div className="opportunity-footer">
            <div>
              <small>Next action</small>
              <strong>Connect your applications source</strong>
            </div>
            <button type="button" className="text-button">
              View <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
