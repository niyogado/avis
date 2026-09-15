import React, { useEffect, useState } from 'react'
import { BookOpen, BrainCircuit, FileText, ShieldCheck } from 'lucide-react'
import apiClient from '../api/config'

export default function Knowledge() {
  const [entries, setEntries] = useState([])

  useEffect(() => {
    let active = true
    apiClient
      .get('/api/ai/training')
      .then((res) => {
        if (!active) return
        const items = (res.data || []).map((item) => ({
          title: item.title || 'Career update',
          detail: item.content || 'No detail provided.',
          tag: item.is_active ? 'Approved' : 'Review',
        }))
        setEntries(items.length ? items : [{ title: 'No approved context yet', detail: 'Add a training insight or CV update to teach AVIS about your work.', tag: 'Waiting' }])
      })
      .catch(() => {
        if (active) setEntries([{ title: 'No approved context yet', detail: 'No training notes are available yet for this user.', tag: 'Waiting' }])
      })

    return () => { active = false }
  }, [])

  return (
    <div className="page-shell">
      <div className="section-head narrow">
        <div>
          <div className="eyebrow">KNOWLEDGE</div>
          <h1>Professional memory</h1>
        </div>
      </div>

      <div className="stack-list">
        {entries.map((item) => (
          <div key={item.title} className="panel" style={{ padding: '18px 20px' }}>
            <div className="opportunity-header">
              <div className="title-line">
                <span className="mini-icon">
                  {item.tag === 'Approved' ? <BrainCircuit size={16} /> : item.tag === 'Review' ? <FileText size={16} /> : <BookOpen size={16} />}
                </span>
                <div>
                  <strong>{item.title}</strong>
                  <small>{item.detail}</small>
                </div>
              </div>
              <span className="status-badge"><ShieldCheck size={12} /> {item.tag}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
