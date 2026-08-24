import React, { useEffect, useState } from 'react'
import { AlertCircle, Bell, Brain, User as UserIcon } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import apiClient from '../api/config'
import Loader from '../components/Loader'

const inputStyle = {
  borderRadius: 12,
  border: '1px solid var(--border)',
  padding: '10px 12px',
  background: 'rgba(255,255,255,0.4)',
  color: 'var(--text)',
}

const toggleBtnStyle = {
  width: 44,
  height: 24,
  borderRadius: 999,
  cursor: 'pointer',
  border: '1px solid var(--border-strong)',
  position: 'relative',
}

const emptySettings = {
  ai_provider: 'auto',
  ai_model: '',
  ai_fallback_enabled: true,
  ai_response_style: 'balanced',
  notify_job_alerts: true,
  notify_application_updates: true,
  notify_career_recommendations: true,
  notify_system: true,
}

export default function Settings() {
  const { user, logout } = useAuth()
  const [settings, setSettings] = useState({ ...emptySettings })
  const [aiOptions, setAiOptions] = useState({ providers: [], models: {}, response_styles: [], availability: {} })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [savedMsg, setSavedMsg] = useState('')
  const [errorMsg, setErrorMsg] = useState('')

  useEffect(() => {
    setLoading(true)
    Promise.all([
      apiClient.get('/api/settings/').catch(() => ({ data: null })),
      apiClient.get('/api/settings/ai-options').catch(() => ({ data: null })),
    ])
      .then(([settingsRes, aiRes]) => {
        setSettings({ ...emptySettings, ...(settingsRes?.data || {}) })
        setAiOptions(aiRes?.data || { providers: [], models: {}, response_styles: [], availability: {} })
      })
      .catch(() => setErrorMsg('Unable to load your settings.'))
      .finally(() => setLoading(false))
  }, [])

  const updateSetting = (patch) => setSettings((current) => ({ ...current, ...patch }))

  const changeProvider = (provider) => {
    setSettings((current) => ({
      ...current,
      ai_provider: provider,
      ai_model: provider === 'auto' ? '' : (aiOptions.models[provider] || [])[0] || '',
    }))
  }

  const toggle = (key) => updateSetting({ [key]: !settings[key] })

  const save = async () => {
    setSaving(true)
    setErrorMsg('')
    setSavedMsg('')
    try {
      await apiClient.put('/api/settings/', settings)
      setSavedMsg('Settings saved. AVIS now uses your provider and style selection.')
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Could not save settings.')
    } finally {
      setSaving(false)
    }
  }

  const Toggle = ({ label, checked, onChange, icon }) => (
    <div className="list-row" style={{ justifyContent: 'space-between', gap: 14, padding: '8px 0' }}>
      <strong style={{ display: 'flex', alignItems: 'center', gap: 8 }}>{icon}{label}</strong>
      <button
        type="button"
        onClick={onChange}
        aria-pressed={Boolean(checked)}
        style={{ ...toggleBtnStyle, background: checked ? 'var(--accent)' : 'rgba(255,255,255,0.35)' }}
      >
        <span
          style={{
            position: 'absolute',
            top: 2,
            left: checked ? 22 : 2,
            width: 20,
            height: 20,
            borderRadius: 999,
            background: '#fff',
          }}
        />
      </button>
    </div>
  )

  if (loading) {
    return <Loader variant="fetch" title="Loading settings..." message="Checking your AI and notification preferences." />
  }

  return (
    <div className="page-shell">
      <div className="section-head narrow">
        <div>
          <div className="eyebrow">SETTINGS</div>
          <h1>How AVIS works for you</h1>
        </div>
        <div className="quick-actions">
          <button type="button" className="primary-button" onClick={save} disabled={saving}>{saving ? 'Saving…' : 'Save settings'}</button>
          <button type="button" className="secondary-button" onClick={logout}>Sign out</button>
        </div>
      </div>

      {savedMsg && <div className="form-message" style={{ marginBottom: 10, color: '#22c55e' }}>{savedMsg}</div>}
      {errorMsg && <div className="form-message error" style={{ marginBottom: 10 }}>{errorMsg}</div>}

      <div className="panel" style={{ padding: '20px' }}>
        <div className="cv-section-title"><Brain size={16} /><strong>AI Provider</strong></div>
        <p className="cv-empty-copy" style={{ marginTop: 6 }}>Only providers and models tested by AVIS are shown. API keys stay on the server.</p>
        <div className="tag-row" style={{ marginTop: 12 }}>
          {(aiOptions.providers || ['auto', 'ejochat', 'huggingface']).map((provider) => (
            <button
              key={provider}
              type="button"
              className={settings.ai_provider === provider ? 'primary-button' : 'secondary-button'}
              onClick={() => changeProvider(provider)}
            >
              {provider}{aiOptions.availability[provider] === false ? ' · not configured' : ''}
            </button>
          ))}
        </div>

        <div style={{ marginTop: 14 }}>
          <div className="mini-label">AI MODEL</div>
          <select
            value={settings.ai_model}
            onChange={(e) => updateSetting({ ai_model: e.target.value })}
            disabled={settings.ai_provider === 'auto'}
            style={inputStyle}
          >
            {settings.ai_provider === 'auto' ? (
              <option value="">Auto (EjoChat primary, Hugging Face backup)</option>
            ) : (
              (aiOptions.models[settings.ai_provider] || [settings.ai_model]).map((model) => (
                <option key={model} value={model}>{model}</option>
              ))
            )}
          </select>
          {settings.ai_provider === 'auto' && (
            <p className="cv-empty-copy" style={{ marginTop: 6 }}>Auto uses EjoChat first, then falls back to Hugging Face only when configured.</p>
          )}
        </div>

        <Toggle
          label="Use a backup provider if the selected one is unavailable"
          checked={settings.ai_fallback_enabled}
          onChange={() => toggle('ai_fallback_enabled')}
          icon={<AlertCircle size={14} />}
        />

        <div style={{ marginTop: 12 }}>
          <div className="mini-label">AI RESPONSE STYLE</div>
          <div className="tag-row">
            {(aiOptions.response_styles || ['concise', 'balanced', 'detailed']).map((style) => (
              <button key={style} type="button" className={settings.ai_response_style === style ? 'primary-button' : 'secondary-button'} onClick={() => updateSetting({ ai_response_style: style })}>
                {style}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="panel" style={{ padding: '20px' }}>
        <div className="cv-section-title"><Bell size={16} /><strong>Notifications</strong></div>
        <div style={{ display: 'grid', gap: 10, marginTop: 10 }}>
          <Toggle label="Job alerts" checked={settings.notify_job_alerts} onChange={() => toggle('notify_job_alerts')} />
          <Toggle label="Application updates" checked={settings.notify_application_updates} onChange={() => toggle('notify_application_updates')} />
          <Toggle label="Career recommendations" checked={settings.notify_career_recommendations} onChange={() => toggle('notify_career_recommendations')} />
          <Toggle label="AI / system notifications" checked={settings.notify_system} onChange={() => toggle('notify_system')} />
        </div>
      </div>

      <div className="panel" style={{ padding: '20px' }}>
        <div className="cv-section-title"><UserIcon size={16} /><strong>Account</strong></div>
        <div className="stack-list">
          {user ? (
            <div className="list-row" style={{ marginTop: 10 }}><strong>Signed in</strong><span>{user.email || 'AVIS user'}</span></div>
          ) : (
            <p className="cv-empty-copy">No account signed in.</p>
          )}
          <div className="list-row" style={{ marginTop: 8 }}><strong>Password &amp; security</strong><span>Managed by your identity provider</span></div>
        </div>
      </div>
    </div>
  )
}