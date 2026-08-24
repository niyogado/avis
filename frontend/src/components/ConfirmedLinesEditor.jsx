import React, { useState } from 'react'
import { BadgeCheck, Plus, X } from 'lucide-react'

const inputStyle = {
  borderRadius: 12,
  border: '1px solid var(--border)',
  padding: '10px 12px',
  background: 'rgba(255,255,255,0.4)',
  color: 'var(--text)',
}

/**
 * Reusable "line item" editor for confirmed sections
 * (experience / education / projects / certifications / achievements).
 * Each line is a free-text entry the user has reviewed/confirmed; the
 * "suggested" prop powers the "You may confirm" hints that come from the
 * CV/AI analysis, with clear separation from confirmed values.
 */
export default function ConfirmedLinesEditor({
  label,
  items,
  suggested = [],
  onChange,
  max = 12,
  placeholder = 'Add a line…',
  hintTitle = 'From your CV (confirm to accept)',
}) {
  const [draft, setDraft] = useState('')

  const remove = (value) => onChange(items.filter((item) => item !== value))

  const add = (value) => {
    const clean = (value ?? '').trim()
    if (!clean) return
    if (items.includes(clean)) return
    onChange([...items, clean].slice(0, max))
    setDraft('')
  }

  // Suggested entries that are not already confirmed.
  const availableSuggestions = (suggested || []).filter((s) => !items.includes(s))

  return (
    <div style={{ marginBottom: 14 }}>
      <div className="mini-label">{label}</div>
      {items.length === 0 && availableSuggestions.length === 0 ? (
        <p className="cv-empty-copy">{`No ${label.toLowerCase()} yet.`}</p>
      ) : (
        <div className="evidence-list" style={{ display: 'grid', gap: 8 }}>
          {items.map((item) => (
            <div key={item} className="evidence-row">
              <div className="evidence-main">
                <BadgeCheck size={14} style={{ color: 'var(--accent)' }} />
                <strong>{item}</strong>
              </div>
              <button
                type="button"
                className="inline-button"
                aria-label={`Remove ${item}`}
                onClick={() => remove(item)}
              >
                <X size={13} />
              </button>
            </div>
          ))}
        </div>
      )}

      {availableSuggestions.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <small className="meta-copy">{hintTitle}</small>
          <div className="tag-row" style={{ marginTop: 6 }}>
            {availableSuggestions.map((s) => (
              <button
                key={s}
                type="button"
                className="tag strong"
                style={{ border: '1px solid var(--border)', background: 'transparent' }}
                onClick={() => add(s)}
              >
                {s} <Plus size={12} />
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="quick-actions" style={{ marginTop: 10 }}>
        <input
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              event.preventDefault()
              add(draft)
            }
          }}
          placeholder={placeholder}
          style={{ flex: 1, ...inputStyle, height: 20 }}
        />
        <button type="button" className="secondary-button" onClick={() => add(draft)} disabled={!draft.trim()}>
          <Plus size={13} /> Add
        </button>
      </div>
    </div>
  )
}