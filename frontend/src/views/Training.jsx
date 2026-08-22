import React, { useEffect, useState } from 'react'
import { Brain, CheckCircle2, Clock3, GraduationCap } from 'lucide-react'
import apiClient from '../api/config'

export default function Training() {
  const [draft, setDraft] = useState('')
  const [knowledge, setKnowledge] = useState([])
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')

  const loadKnowledge = async () => {
    try {
      const res = await apiClient.get('/api/ai/training')
      setKnowledge(res.data || [])
    } catch (err) {
      setKnowledge([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadKnowledge()
  }, [])

  const saveTraining = async () => {
    if (!draft.trim()) {
      setError('Add a concrete learning or project update before saving.')
      return
    }

    setSending(true)
    setError('')

    try {
      await apiClient.post('/api/ai/training', {
        title: 'Career update',
        content: draft.trim(),
        category: 'career_intent',
        is_active: true,
      })
      setDraft('')
      await loadKnowledge()
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to save the training note.')
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="page-shell">
      <div className="section-head narrow">
        <div>
          <div className="eyebrow">TRAINING</div>
          <h1>Tell AVIS what your CV cannot.</h1>
        </div>
      </div>

      <div className="panel" style={{ padding: '18px 20px' }}>
        <div className="mini-label">AI PROMPT</div>
        <div className="signal-row strong">
          <GraduationCap size={16} />
          <span>AVIS already understands your CV.</span>
        </div>
        <div style={{ marginTop: 14 }}>
          <textarea
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            rows={5}
            placeholder="What project did you build? What problems did you solve? What changed because of your work?"
            style={{ width: '100%', border: '1px solid var(--border)', borderRadius: '12px', padding: '14px 16px', background: 'rgba(255,255,255,0.4)', color: 'var(--text)' }}
          />
        </div>
        <div className="quick-actions" style={{ marginTop: 14 }}>
          <button type="button" className="primary-button" onClick={saveTraining} disabled={sending}>
            {sending ? 'Saving…' : 'Save insight'}
          </button>
          <button type="button" className="secondary-button">Review knowledge</button>
        </div>
        {error && <div className="form-message error" style={{ marginTop: 12 }}>{error}</div>}
      </div>

      <div className="stack-list">
        {loading ? (
          <div className="panel" style={{ padding: '20px' }}>Loading training notes…</div>
        ) : knowledge.length === 0 ? (
          <div className="panel" style={{ padding: '20px' }}>No training notes yet. Add one to teach AVIS about your recent work.</div>
        ) : (
          knowledge.map((item) => (
            <div key={item.id} className="panel" style={{ padding: '18px 20px' }}>
              <div className="opportunity-header">
                <div className="title-line">
                  <span className="mini-icon"><Brain size={16} /></span>
                  <div>
                    <strong>{item.title || 'Career update'}</strong>
                    <small>{item.category || 'career_intent'}</small>
                  </div>
                </div>
                <span className={`status-badge ${item.is_active ? '' : 'soft'}`}>
                  {item.is_active ? <CheckCircle2 size={12} /> : <Clock3 size={12} />}
                  {item.is_active ? 'Approved' : 'Review'}
                </span>
              </div>
              <div style={{ marginTop: 12, color: 'var(--text-soft)', lineHeight: 1.7 }}>{item.content}</div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
