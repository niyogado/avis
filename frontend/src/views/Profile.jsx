import React, { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import apiClient from '../api/config'

export default function Profile() {
  const { token, user, setUser } = useAuth()
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    full_name: '',
    headline: '',
    location: '',
    phone: '',
    summary: '',
    avatar_url: '',
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')
  const [successMsg, setSuccessMsg] = useState('')
  const [avatarPreview, setAvatarPreview] = useState(null)

  useEffect(() => {
    if (!token) {
      setErrorMsg('Not logged in. Please log in to view your profile.')
      setLoading(false)
      return
    }

    apiClient.get('/api/profile/')
      .then((res) => {
        const p = res.data || {}
        setForm({
          first_name: p.first_name || '',
          last_name: p.last_name || '',
          full_name: p.full_name || '',
          headline: p.headline || '',
          location: p.location || '',
          phone: p.phone || '',
          summary: p.summary || '',
          avatar_url: p.avatar_url || '',
        })
        setAvatarPreview(p.avatar_url || null)
      })
      .catch((err) => {
        console.error('Profile fetch error:', err.response || err)
        setErrorMsg(err.response?.data?.detail || 'Could not load profile.')
      })
      .finally(() => setLoading(false))
  }, [token])

  const handleChange = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleAvatarFile = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      setAvatarPreview(reader.result)
      setForm(f => ({ ...f, avatar_url: reader.result }))
    }
    reader.readAsDataURL(file)
  }

  const save = async () => {
    setSaving(true)
    setErrorMsg('')
    setSuccessMsg('')
    try {
      const fullName = [form.first_name, form.last_name].filter(Boolean).join(' ') || form.full_name
      const payload = {
        first_name: form.first_name,
        last_name: form.last_name,
        full_name: fullName || form.full_name,
        headline: form.headline,
        location: form.location,
        phone: form.phone,
        summary: form.summary,
        avatar_url: form.avatar_url,
      }
      const res = await apiClient.put('/api/profile/', payload)
      setSuccessMsg('Profile saved')
      if (res.data) setUser(res.data)
    } catch (err) {
      console.error('Save profile error', err.response || err)
      setErrorMsg(err.response?.data?.detail || 'Failed to save profile')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="text-[rgba(243,241,233,0.6)]">Loading your profile...</div>

  return (
    <div className="max-w-3xl mx-auto mt-8">
      <h1 className="text-2xl font-bold mb-4 text-[#F3F1E9]">My Profile</h1>

      {errorMsg && (
        <div className="p-3 mb-4 rounded bg-[rgba(217,106,28,0.15)] text-[#D96A1C] border border-[rgba(217,106,28,0.3)]">
          {errorMsg}
        </div>
      )}

      {successMsg && (
        <div className="p-3 mb-4 rounded bg-[rgba(34,197,94,0.08)] text-[#22c55e] border border-[rgba(34,197,94,0.12)]">
          {successMsg}
        </div>
      )}

      <div className="panel p-6 rounded bg-[#191915] text-[#F3F1E9] border border-[rgba(243,241,233,0.12)]">
        <div className="flex gap-6">
          <div className="w-36 flex flex-col items-center">
            {avatarPreview ? (
              <img src={avatarPreview} alt="avatar" className="w-28 h-28 rounded-full object-cover" />
            ) : (
              <div className="w-28 h-28 rounded-full bg-[#D96A1C] flex items-center justify-center text-white text-xl font-semibold">{(form.full_name || 'U').split(' ').map(n => n[0]).slice(0, 2).join('')}</div>
            )}
            <label className="mt-3 text-sm text-[rgba(243,241,233,0.8)] cursor-pointer">
              Change avatar
              <input type="file" accept="image/*" onChange={handleAvatarFile} className="hidden" />
            </label>
            <div className="mt-2 text-xs text-[rgba(243,241,233,0.6)]">PNG, JPG — keep it professional</div>
          </div>

          <div className="flex-1">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-[rgba(243,241,233,0.6)]">First name</label>
                <input value={form.first_name} onChange={handleChange('first_name')} className="w-full p-2 rounded mt-1 bg-[#0E0E0C] border border-[rgba(243,241,233,0.06)]" />
              </div>
              <div>
                <label className="text-sm text-[rgba(243,241,233,0.6)]">Last name</label>
                <input value={form.last_name} onChange={handleChange('last_name')} className="w-full p-2 rounded mt-1 bg-[#0E0E0C] border border-[rgba(243,241,233,0.06)]" />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div>
                <label className="text-sm text-[rgba(243,241,233,0.6)]">Full name</label>
                <input value={form.full_name} onChange={handleChange('full_name')} className="w-full p-2 rounded mt-1 bg-[#0E0E0C] border border-[rgba(243,241,233,0.06)]" />
              </div>
              <div>
                <label className="text-sm text-[rgba(243,241,233,0.6)]">Headline</label>
                <input value={form.headline} onChange={handleChange('headline')} className="w-full p-2 rounded mt-1 bg-[#0E0E0C] border border-[rgba(243,241,233,0.06)]" />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div>
                <label className="text-sm text-[rgba(243,241,233,0.6)]">Location</label>
                <input value={form.location} onChange={handleChange('location')} className="w-full p-2 rounded mt-1 bg-[#0E0E0C] border border-[rgba(243,241,233,0.06)]" />
              </div>
              <div>
                <label className="text-sm text-[rgba(243,241,233,0.6)]">Phone</label>
                <input value={form.phone} onChange={handleChange('phone')} className="w-full p-2 rounded mt-1 bg-[#0E0E0C] border border-[rgba(243,241,233,0.06)]" />
              </div>
            </div>

            <div className="mt-4">
              <label className="text-sm text-[rgba(243,241,233,0.6)]">Summary</label>
              <textarea value={form.summary} onChange={handleChange('summary')} rows={6} className="w-full p-2 rounded mt-1 bg-[#0E0E0C] border border-[rgba(243,241,233,0.06)]" />
            </div>

            <div className="mt-4 flex items-center gap-3">
              <button onClick={save} disabled={saving} className="px-4 py-2 bg-[#D96A1C] text-white rounded">{saving ? 'Saving...' : 'Save profile'}</button>
              <button onClick={() => {
                setLoading(true)
                apiClient.get('/api/profile/')
                  .then(r => {
                    const p = r.data || {}
                    setForm({
                      first_name: p.first_name || '',
                      last_name: p.last_name || '',
                      full_name: p.full_name || '',
                      headline: p.headline || '',
                      location: p.location || '',
                      phone: p.phone || '',
                      summary: p.summary || '',
                      avatar_url: p.avatar_url || '',
                    })
                    setAvatarPreview(p.avatar_url || null)
                  })
                  .finally(() => setLoading(false))
              }} className="px-3 py-1 border rounded border-[rgba(243,241,233,0.06)]">Discard</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}