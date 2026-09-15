import React, { useState } from 'react'
import { ArrowUp, Paperclip, Sparkles } from 'lucide-react'
import apiClient from '../api/config'

const initialMessages = [
  { role: 'assistant', content: 'Ask about your profile, evidence, strengths, or next career steps.' },
]

export default function Chat() {
  const [messages, setMessages] = useState(initialMessages)
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)

  const sendMessage = async () => {
    const value = draft.trim()
    if (!value || sending) return

    const userMessage = { role: 'user', content: value }
    setMessages((current) => [...current, userMessage])
    setDraft('')
    setSending(true)

    try {
      const res = await apiClient.post('/api/ai/chat', { message: value })
      const response = res.data?.response || 'I could not generate a response from the current AI configuration.'
      setMessages((current) => [...current, { role: 'assistant', content: response }])
    } catch (error) {
      setMessages((current) => [
        ...current,
        { role: 'assistant', content: error.response?.data?.detail || 'The AI service is not available right now. Please try again later.' },
      ])
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="page-shell">
      <div className="section-head narrow">
        <div>
          <div className="eyebrow">CHAT</div>
          <h1>Your professional AI</h1>
        </div>
      </div>

      <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '18px 20px', borderBottom: '1px solid var(--border)' }}>
          <div className="signal-row muted">
            <Sparkles size={14} />
            <span>Grounded in your approved profile and training context.</span>
          </div>
        </div>

        <div style={{ padding: '18px 20px', display: 'grid', gap: 12 }}>
          {messages.map((message, index) => (
            <div key={`${message.role}-${index}`} style={{ maxWidth: message.role === 'assistant' ? '78%' : '50%', marginLeft: message.role === 'assistant' ? 0 : 'auto' }} className="panel" aria-label={message.role}>
              <div style={{ padding: '12px 14px', lineHeight: 1.7, color: 'var(--text)' }}>
                {message.content}
              </div>
            </div>
          ))}
        </div>

        <div style={{ padding: '12px 18px 18px', display: 'flex', gap: 10, borderTop: '1px solid var(--border)' }}>
          <button type="button" className="icon-button" aria-label="Attach file"><Paperclip size={14} /></button>
          <input
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="Ask AVIS anything about your professional identity..."
            style={{ flex: 1, borderRadius: 12, border: '1px solid var(--border)', background: 'rgba(255,255,255,0.4)', padding: '11px 12px', color: 'var(--text)' }}
            onKeyDown={(event) => {
              if (event.key === 'Enter') {
                event.preventDefault()
                sendMessage()
              }
            }}
          />
          <button type="button" className="primary-button" onClick={sendMessage} disabled={sending}>
            <ArrowUp size={14} />
          </button>
        </div>
      </div>
    </div>
  )
}
