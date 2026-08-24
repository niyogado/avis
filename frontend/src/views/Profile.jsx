import React, { useEffect, useState } from 'react'
import { BadgeCheck, FileText, User } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import apiClient from '../api/config'
import ConfirmedLinesEditor from '../components/ConfirmedLinesEditor'
import Loader from '../components/Loader'

const LEVELS = ['student', 'entry-level', 'junior', 'mid', 'senior', 'lead', 'principal']
const WORK_PREFERENCES = ['remote', 'hybrid', 'onsite', 'flexible']

const inputStyle = {
  borderRadius: 12,
  border: '1px solid var(--border)',
  padding: '10px 12px',
  background: 'rgba(255,255,255,0.4)',
  color: 'var(--text)',
}

const emptyContext = {
  professional_level: '',
  primary_role: '',
  target_roles: [],
  confirmed_skills: [],
  career_interests: [],
  preferred_locations: [],
  work_preference: '',
  experience: [],
  education: [],
  projects: [],
  certifications: [],
  achievements: [],
  career_goals: '',
}

function ChipBuilder({ field, value, onChange, suggested = [], max = 6 }) {
  const add = (term) => {
    const clean = term.trim()
    if (!clean) return
    if (value.includes(clean) || value.length >= max) return
    onChange([...value, clean])
  }
  const remove = (term) => onChange(value.filter((item) => item !== term))
  const available = suggested.filter((item) => !value.includes(item))
  return (
    <div>
      {value.length > 0 && (
        <div className="tag-row">
          {value.map((item) => (
            <button key={item} type="button" className="tag strong" onClick={() => remove(item)}>
              {item} ✕
            </button>
          ))}
        </div>
      )}
      {available.length > 0 && (
        <div className="tag-row" style={{ marginTop: 8 }}>
          {available.slice(0, 8).map((s) => (
            <button key={s} type="button" className="tag soft" onClick={() => add(s)}>
              {s} +
            </button>
          ))}
        </div>
      )}
      <AddInput placeholder={field === 'preferred_locations' ? 'e.g. Kigali or Remote' : 'Add…'} value="" onAdd={add} />
    </div>
  )
}

function AddInput({ placeholder, value, onAdd }) {
  const [draft, setDraft] = useState(value)
  return (
    <div className="quick-actions" style={{ marginTop: 8 }}>
      <input
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            e.preventDefault()
            onAdd(draft)
            setDraft('')
          }
        }}
        placeholder={placeholder}
        style={{ flex: 1, ...inputStyle, height: 24 }}
      />
      <button type="button" className="inline-button" onClick={() => { onAdd(draft); setDraft('') }}>
        Add
      </button>
    </div>
  )
}

export default function Profile() {
  const { user, setUser, logout } = useAuth()
  const [form, setForm] = useState({ first_name: '', last_name: '', full_name: '', headline: '', summary: '', location: '', phone: '' })
  const [identity, setIdentity] = useState({ ...emptyContext })
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [mode, setMode] = useState('identity')
  const [saving, setSaving] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')
  const [successMsg, setSuccessMsg] = useState('')

  useEffect(() => {
    setLoading(true)
    setErrorMsg('')

    Promise.all([
      apiClient.get('/api/profile/').catch(() => ({ data: null })),
      apiClient.get('/api/profile/professional-context').catch(() => ({ data: null })),
      apiClient.get('/api/cv/').catch(() => ({ data: [] })),
    ])
      .then(([pRes, ctxRes, cvRes]) => {
        const p = pRes?.data || {}
        setForm({
          first_name: p.first_name || '',
          last_name: p.last_name || '',
          full_name: p.full_name || '',
          headline: p.headline || '',
          summary: p.summary || '',
          location: p.location || '',
          phone: p.phone || '',
        })
        const ctx = ctxRes?.data || {}
        // Merge so partial stored confirmations don't wipe empty optional fields.
        setIdentity({ ...emptyContext, ...ctx })
        setAnalysis((cvRes?.data || [])[0]?.analysis_json || null)
      })
      .catch(() => setErrorMsg('Unable to load your profile.'))
      .finally(() => setLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const updateForm = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }))
  const updateIdentity = (patch) => setIdentity((current) => ({ ...current, ...patch }))

  const saveForm = async () => {
    setSaving(true)
    setErrorMsg('')
    setSuccessMsg('')
    const fullName = [form.first_name, form.last_name].filter(Boolean).join(' ') || form.full_name
    try {
      const res = await apiClient.put('/api/profile/', {
        first_name: form.first_name,
        last_name: form.last_name,
        full_name: fullName,
        headline: form.headline,
        summary: form.summary,
        location: form.location,
        phone: form.phone,
      })
      if (res.data?.full_name && typeof setUser === 'function') {
        setUser((u) => ({ ...(u || {}), full_name: res.data.full_name }))
      }
      setSuccessMsg('Basic information saved.')
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Could not save basic information.')
    } finally {
      setSaving(false)
    }
  }

  const saveIdentity = async () => {
    setSaving(true)
    setErrorMsg('')
    setSuccessMsg('')
    try {
      await apiClient.put('/api/profile/professional-context', identity)
      setSuccessMsg('Professional identity confirmed. AVIS now uses it in Chat, Career Intelligence, CV Writer, and Opportunities.')
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Could not save your professional identity.')
    } finally {
      setSaving(false)
    }
  }

  const evidence = analysis?.cv_evidence || {}
  const interp = analysis?.ai_interpretation || {}
  const suggestedDirections = interp.career_directions || []
  const suggestedSkills = evidence.skills || []
  const hasAnalysis = Boolean(analysis)

  if (loading) {
    return <Loader variant="fetch" title="Loading your profile..." message="Building your confirmed professional identity." />
  }

  return (
    <div className="page-shell">
      <div className="section-head">
        <div>
          <div className="eyebrow">PROFILE</div>
          <h1>{form.full_name || 'Your professional identity'}</h1>
        </div>
        <div className="quick-actions">
          <button type="button" className={`inline-button ${mode === 'information' ? 'active' : ''}`} onClick={() => setMode('information')}>Information</button>
          <button type="button" className={`inline-button ${mode === 'identity' ? 'active' : ''}`} onClick={() => setMode('identity')}>Identity</button>
          <button type="button" className="secondary-button" onClick={logout}>Sign out</button>
        </div>
      </div>

      {errorMsg && <div className="form-message error" style={{ marginBottom: 10 }}>{errorMsg}</div>}
      {successMsg && <div className="form-message" style={{ marginBottom: 10, color: '#22c55e' }}>{successMsg}</div>}

      {mode === 'information' ? (
        <div className="panel" style={{ padding: '18px 20px' }}>
          <div className="cv-section-title"><User size={16} /><strong>Basic information</strong></div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0,1fr))', gap: 12, marginTop: 14 }}>
            <label style={{ display: 'grid', gap: 6 }}><small>First name</small><input value={form.first_name} onChange={updateForm('first_name')} style={inputStyle} /></label>
            <label style={{ display: 'grid', gap: 6 }}><small>Last name</small><input value={form.last_name} onChange={updateForm('last_name')} style={inputStyle} /></label>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 12, marginTop: 12 }}>
            <label style={{ display: 'grid', gap: 6 }}><small>Professional title</small><input value={form.headline} onChange={updateForm('headline')} placeholder="e.g. Senior Backend Developer" style={inputStyle} /></label>
            <label style={{ display: 'grid', gap: 6 }}><small>Location</small><input value={form.location} onChange={updateForm('location')} placeholder="e.g. Kigali, Rwanda" style={inputStyle} /></label>
          </div>
          <label style={{ display: 'grid', gap: 6, marginTop: 12 }}><small>Professional summary</small><textarea value={form.summary} onChange={updateForm('summary')} rows={5} style={inputStyle} /></label>

          <div className="quick-actions" style={{ marginTop: 18 }}>
            <button type="button" className="primary-button" onClick={saveForm} disabled={saving}>{saving ? 'Saving…' : 'Save information'}</button>
            <button type="button" className="secondary-button" onClick={() => setMode('identity')}>Edit professional identity</button>
          </div>
        </div>
      ) : (
        <div className="panel" style={{ padding: '20px' }}>
          <div className="cv-section-title"><BadgeCheck size={16} /><strong>Confirmed professional identity — who you are</strong></div>
          <p className="cv-empty-copy" style={{ marginTop: 6 }}>
            Your confirmation overrides AI suggestions. Values below feed Chat, Career Intelligence, CV Writer, and Opportunities.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px,1fr))', gap: 12, marginTop: 14 }}>
            <label style={{ display: 'grid', gap: 6 }}><small>Professional level</small>
              <select value={identity.professional_level || ''} onChange={(e) => updateIdentity({ professional_level: e.target.value || null })} style={inputStyle}>
                <option value="">Not confirmed</option>
                {LEVELS.map((level) => <option key={level} value={level}>{level}</option>)}
              </select>
            </label>
            <label style={{ display: 'grid', gap: 6 }}><small>Primary role</small><input value={identity.primary_role || ''} onChange={(e) => updateIdentity({ primary_role: e.target.value })} placeholder="e.g. Backend Developer" style={inputStyle} /></label>
            <label style={{ display: 'grid', gap: 6 }}><small>Work preference</small><select value={identity.work_preference || ''} onChange={(e) => updateIdentity({ work_preference: e.target.value || null })} style={inputStyle}>
              <option value="">Not confirmed</option>
              {WORK_PREFERENCES.map((pref) => <option key={pref} value={pref}>{pref}</option>)}
            </select></label>
          </div>

          <div style={{ marginTop: 16 }}><div className="mini-label">TARGET ROLES</div><ChipBuilder field="target_roles" value={identity.target_roles} onChange={(list) => updateIdentity({ target_roles: list })} suggested={suggestedDirections} /></div>
          <div style={{ marginTop: 16 }}><div className="mini-label">CONFIRMED SKILLS</div><ChipBuilder field="confirmed_skills" value={identity.confirmed_skills} onChange={(list) => updateIdentity({ confirmed_skills: list })} suggested={suggestedSkills} max={20} /></div>
          <div style={{ marginTop: 16 }}><div className="mini-label">CAREER INTERESTS</div><ChipBuilder field="career_interests" value={identity.career_interests} onChange={(list) => updateIdentity({ career_interests: list })} suggested={(interp.career_directions || []).slice(0, 4)} /></div>
          <div style={{ marginTop: 16 }}><div className="mini-label">PREFERRED LOCATIONS</div><ChipBuilder field="preferred_locations" value={identity.preferred_locations} onChange={(list) => updateIdentity({ preferred_locations: list })} suggested={(form.location ? [form.location] : []).filter(Boolean)} /></div>

          <div className="cv-evidence-band" style={{ marginTop: 20 }}>
            <span>CV-SUGGESTED DETAIL</span>
            <small>Confirm these from your analyzed CV to make them part of your confirmed identity.</small>
          </div>
          <ConfirmedLinesEditor label="Experience" items={identity.experience} suggested={evidence.experience || []} onChange={(list) => updateIdentity({ experience: list })} />
          <ConfirmedLinesEditor label="Education" items={identity.education} suggested={evidence.education || []} onChange={(list) => updateIdentity({ education: list })} />
          <ConfirmedLinesEditor label="Projects" items={identity.projects} suggested={evidence.projects || []} onChange={(list) => updateIdentity({ projects: list })} />
          <ConfirmedLinesEditor label="Certifications" items={identity.certifications} suggested={evidence.certifications || []} onChange={(list) => updateIdentity({ certifications: list })} />
          <ConfirmedLinesEditor label="Achievements" items={identity.achievements} suggested={evidence.achievements || []} onChange={(list) => updateIdentity({ achievements: list })} />

          <div style={{ marginTop: 16 }}><div className="mini-label">CAREER GOALS</div><textarea value={identity.career_goals || ''} onChange={(e) => updateIdentity({ career_goals: e.target.value })} rows={3} placeholder="e.g. I want to grow into a lead engineer within three years." style={inputStyle} /></div>

          <div className="quick-actions" style={{ marginTop: 20 }}>
            <button type="button" className="primary-button" onClick={saveIdentity} disabled={saving}>
              {saving ? 'Saving…' : 'Confirm professional identity'}
            </button>
            <span className="status-badge soft"><BadgeCheck size={12} /> Confirmation overrides AI suggestions</span>
          </div>
        </div>
      )}
    </div>
  )
}