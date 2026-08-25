import React, { useState } from 'react';
import { chatService } from '../services/chatService';
import { Card } from '../components/Card';
import { Loader } from '../components/Loader';

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);

  const send = async (e) => {
    e?.preventDefault();
    if (!input.trim()) return;
    setSending(true);
    setError(null);
    const userMsg = { id: Date.now(), role: 'user', text: input };
    setMessages((m) => [...m, userMsg]);
    setInput('');
    try {
      const res = await chatService.sendMessage(input);
      setMessages((m) => [...m, { id: Date.now() + 1, role: 'ai', text: res?.reply || 'No response' }]);
    } catch (err) {
      setError(err?.message || 'Chat failed');
    } finally {
      setSending(false);
    }
  };

  return (
    <div>
      <div className="header-row">
        <div>
          <h1 className="h1">AI Chat</h1>
          <div className="p-muted">Ask AVIS assistant for CV tips, job search help and more</div>
        </div>
      </div>

      <Card>
        <div style={{ minHeight: 240, display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ flex: 1, overflowY: 'auto', padding: 8 }}>
            {messages.length === 0 && <div className="small">Start a conversation</div>}
            {messages.map((m) => (
              <div key={m.id} style={{ marginBottom: 8, display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
                <div style={{ background: m.role === 'user' ? 'var(--accent)' : 'rgba(0,0,0,0.06)', color: m.role === 'user' ? '#fff' : 'var(--text)', padding: 10, borderRadius: 10, maxWidth: '70%' }}>
                  {m.text}
                </div>
              </div>
            ))}
          </div>

          {error && <div role="alert" style={{ color: '#d14343' }}>{error}</div>}

          <form onSubmit={send} style={{ display: 'flex', gap: 8 }}>
            <input className="input" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Type a message..." aria-label="Chat input" />
            <button className="btn" type="submit" disabled={sending}>{sending ? <Loader size={16} /> : 'Send'}</button>
          </form>
        </div>
      </Card>
    </div>
  );
}
