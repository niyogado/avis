import React from 'react'
import { ArrowRight, BadgeCheck, PenLine, Sparkles, Wand2 } from 'lucide-react'

const evidence = [
  'Built a FastAPI backend for AVIS',
  'Designed API structures for careers and identity workflows',
  'Used PostgreSQL and structured validation for trusted data',
]

export default function CVWriter() {
  return (
    <div className="page-shell">
      <div className="section-head narrow">
        <div>
          <div className="eyebrow">CV WRITER</div>
          <h1>Professional version</h1>
        </div>
      </div>

      <div className="split-panel">
        <div className="panel" style={{ padding: '20px' }}>
          <div className="mini-label">YOUR EVIDENCE</div>
          <div className="evidence-list">
            {evidence.map((item) => (
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
            Developed a backend API using FastAPI and PostgreSQL for a professional identity and career intelligence platform, improving data quality, retrieval and role-specific AI workflows.
          </p>

          <div className="quick-actions" style={{ marginTop: 18 }}>
            <button type="button" className="primary-button"><BadgeCheck size={14} /> Accept</button>
            <button type="button" className="secondary-button"><PenLine size={14} /> Edit</button>
          </div>
        </div>
      </div>
    </div>
  )
}
