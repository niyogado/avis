import React, { useEffect, useMemo, useState } from 'react'
import { BadgeCheck, Plus, X } from 'lucide-react'
import apiClient from '../api/config'

const LEVELS = ['student', 'entry-level', 'junior', 'mid', 'senior', 'lead', 'principal']
const WORK_PREFERENCES = ['remote', 'hybrid', 'onsite', 'flexible']

const emptyDraft = {
  professional_level: '',
  primary_role: '',
  target_roles: [],
  confirmed_skills: [],
  career_interests: [],
  preferred_locations: [],
  work_preference: '',
}

const inputStyle = {
  borderRadius: 12,
  border: '1px solid var(--border)',
  padding: '10px 12px',
  background: 'rgba(255,255,255,0.4)',
  color: 'var(--text)',
}

const selectStyle = { ...inputStyle }

function sameText(a, b) {
  return String(a || '').trim().toLowerCase() === String(b || '').trim().toLowerCase()
}

export default function ProfessionalIdentityEditor({ analysis }) {
  const [draft, setDraft] = useState(emptyDraft)
  const [loaded, setLoaded] = useState(false)
  const [saving, setSaving] = useState(false)
  const [savedAt, setSavedAt] = useState('')
  const [error, setError] = useState('')
  const [custom, setCustom] = useState({ role: '', skill: '', interest: '', location: '' })

  const evidenceSkills = useMemo(() => analysis?.cv_evidence?.skills || [], [analysis])
  const suggestedDirections = useMemo(() => analysis?.ai_interpretation?.career_directions || [], [analysis])
  const suggestedProfile = analysis?.cv_evidence?.professional_profile || ''

  useEffect(() => {
    let active = true
    apiClient
      .get('/api/profile/professional-context')
      .then((res) => {
        if (!active) return
        setDraft({ ...emptyDraft, ...(res.data || {}) })
        setSavedAt(res.data?.confirmed_at || '')
      })
      .catch(() => {})
      .finally(() => {
        if (active) setLoaded(true)
      })
    return () => {
      active = false
    }
  }, [])

  const update = (patch) => setDraft((current) => ({ ...current, ...patch }))

  const toggleFromList = (field, value) => {
    setDraft((current) => {
      const list = current[field] || []
      return {
        ...current,
        [field]: list.some((entry) => sameText(entry, value))
          ? list.filter((entry) => !sameText(entry, value))
          : [...list, value].slice(0, field === 'confirmed_skills' ? 60 : 10),
      }
    })
  }

  const addCustom = (field, key, max) => {
    const clean = custom[key].trim()
    if (!clean) return
    setCustom((current) => ({ ...current, [key]: '' }))
    setDraft((current) => {
      const list = current[field] || []
      if (list.some((entry) => sameText(entry, clean))) return current
      return { ...current, [field]: [...list, clean].slice(0, max) }
    })
  }

  const removeFrom = (field, value) =>
    update({ [field]: (draft[field] || []).filter((entry) => !sameText(entry, value)) })

  const save = async () => {
    if (saving) return
    setSaving(true)
    setError('')
    try {
      const response = await apiClient.put('/api/profile/professional-context', {
        professional_level: draft.professional_level || null,
        primary_role: draft.primary_role || null,
        target_roles: draft.target_roles,
        confirmed_skills: draft.confirmed_skills,
        career_interests: draft.career_interests,
        preferred_locations: draft.preferred_locations,
        work_preference: draft.work_preference || null,
      })
      setSavedAt(response.data?.confirmed_at || new Date().toISOString())
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to save your professional identity.')
    } finally {
      setSaving(false)
    }
  }

  const levelValue = draft.professional_level || ''
  return (
    <section className="cv-profile-block" style={{ marginTop: 18 }}>
      <div className="cv-section-title">
        <BadgeCheck size={16} />
        <strong>Review &amp; confirm — teach AVIS who you are</strong>
      </div>
      <p className="cv-empty-copy" style={{ marginTop: 6 }}>
        Confirm or correct what AVIS understood. Your confirmations override CV text and AI guesses everywhere.
      </p>

      {suggestedProfile && <div className="mini-label" style={{ marginTop: 10 }}>AVIS UNDERSTANDS</div>}
      {suggestedProfile && <p style={{ marginTop: 6 }}>{suggestedProfile}</p>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginTop: 14 }}>
        <label style={{ display: 'grid', gap: 6 }}>
          <small>Professional level</small>
          <select value={levelValue} onChange={(e) => update({ professional_level: e.target.value || null })} style={selectStyle}>
            <option value="">Not confirmed</option>
            {LEVELS.map((level) => <option key={level} value={level}>{level}</option>)}
          </select>
        </label>
        <label style={{ display: 'grid', gap: 6 }}>
          <small>Primary role today</small>
          <input
            value={draft.primary_role || ''}
            onChange={(e) => update({ primary_role: e.target.value })}
            placeholder="e.g. Backend Developer"
            style={inputStyle}
          />
        </label>
        <label style={{ display: 'grid', gap: 6 }}>
          <small>Work preference</small>
          <select value={draft.work_preference || ''} onChange={(e) => update({ work_preference: e.target.value || null })} style={selectStyle}>
            <option value="">Not confirmed</option>
            {WORK_PREFERENCES.map((pref) => <option key={pref} value={pref}>{pref}</option>)}
          </select>
        </label>
      </div>

      <div style={{ marginTop: 16 }}>
        <div className="mini-label">TARGET ROLES {draft.target_roles.length ? '· ✓ CONFIRMED' : '· TAP TO CONFIRM'}</div>
        <ChipRow
          items={suggestedDirections}
          selected={draft.target_roles}
          onToggle={(value) => toggleFromList('target_roles', value)}
          onRemove={(value) => removeFrom('target_roles', value)}
          removable
        />
        <AddInput placeholder="Add another target role" value={custom.role} setValue={(v) => setCustom((c) => ({ ...c, role: v }))} onAdd={() => addCustom('target_roles', 'role', 8)} />
      </div>

      <div style={{ marginTop: 16 }}>
        <div className="mini-label">SKILLS {draft.confirmed_skills.length ? `· ✓ ${draft.confirmed_skills.length} CONFIRMED` : '· CONFIRM THE REAL ONES'}</div>
        <ChipRow
          items={evidenceSkills.slice(0, 30)}
          selected={draft.confirmed_skills}
          onToggle={(value) => toggleFromList('confirmed_skills', value)}
          onRemove={(value) => removeFrom('confirmed_skills', value)}
          removable
        />
        <AddInput placeholder="Add a skill AVIS missed" value={custom.skill} setValue={(v) => setCustom((c) => ({ ...c, skill: v }))} onAdd={() => addCustom('confirmed_skills', 'skill', 60)} />
      </div>

      <div style={{ marginTop: 16 }}>
        <div className="mini-label">CAREER INTERESTS</div>
        <ChipRow items={[]} selected={draft.career_interests} onToggle={() => {}} onRemove={(value) => removeFrom('career_interests', value)} removable />
        <AddInput placeholder="e.g. AI Engineering" value={custom.interest} setValue={(v) => setCustom((c) => ({ ...c, interest: v }))} onAdd={() => addCustom('career_interests', 'interest', 8)} />
      </div>

      <div style={{ marginTop: 16 }}>
        <div className="mini-label">PREFERRED LOCATIONS</div>
        <ChipRow items={[]} selected={draft.preferred_locations} onToggle={() => {}} onRemove={(value) => removeFrom('preferred_locations', value)} removable />
        <AddInput placeholder="e.g. Kigali or Remote" value={custom.location} setValue={(v) => setCustom((c) => ({ ...c, location: v }))} onAdd={() => addCustom('preferred_locations', 'location', 10)} />
      </div>

      <div className="quick-actions" style={{ marginTop: 18 }}>
        <button type="button" className="primary-button" onClick={save} disabled={saving}>
          {saving ? 'Saving…' : savedAt ? 'Update confirmations' : 'Confirm my professional identity'}
        </button>
        {savedAt && <span className="status-badge"><BadgeCheck size={12} /> Confirmed</span>}
      </div>
      {error && <p className="cv-empty-copy" style={{ color: '#D96A1C' }}>{error}</p>}
    </section>
  )
}

function ChipRow({ items, selected, onToggle, onRemove, removable }) {
  if (!items.length && !selected.length) return null
  const all = [...selected]
  for (const item of items) {
    if (!all.some((entry) => sameText(entry, item))) all.push(item)
  }
  return (
    <div className="tag-row" style={{ marginTop: 8 }}>
      {all.map((item) => {
        const isOn = selected.some((entry) => sameText(entry, item))
        return (
          <button
            key={item}
            type="button"
            className={isOn ? 'tag strong' : 'tag soft'}
            style={{ cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 6 }}
            onClick={() => onToggle(item)}
          >
            {isOn ? <BadgeCheck size={12} /> : null}
            {item}
            {removable && isOn ? (
              <X
                size={11}
                onClick={(event) => {
                  event.stopPropagation()
                  onRemove(item)
                }}
              />
            ) : null}
          </button>
        )
      })}
    </div>
  )
}

function AddInput({ placeholder, value, setValue, onAdd }) {
  return (
    <div className="quick-actions" style={{ marginTop: 8 }}>
      <input
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === 'Enter') {
            event.preventDefault()
            onAdd()
          }
        }}
        placeholder={placeholder}
        style={{ flex: 1, minWidth: 160, borderRadius: 12, border: '1px solid var(--border)', padding: '8px 10px', background: 'rgba(255,255,255,0.4)', color: 'var(--text)' }}
      />
      <button type="button" className="inline-button" onClick={onAdd} disabled={!value.trim()}>
        <Plus size={12} /> Add
      </button>
    </div>
  )
}
