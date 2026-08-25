import React, { useEffect, useState } from 'react';
import { profileService } from '../services/profileService';
import { useApiState } from '../hooks/useApiState';
import { Card } from '../components/Card';
import { Input } from '../components/Input';
import { Button } from '../components/Button';

export default function Profile() {
  const { loading, data, error } = useApiState(() => profileService.get(), []);
  const [form, setForm] = useState({ first_name: '', last_name: '', headline: '', about: '', skills: [] });
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    if (data) setForm({ ...form, ...data });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data]);

  const save = async (e) => {
    e?.preventDefault();
    setSaving(true);
    setSaveError(null);
    setSuccess(null);
    try {
      await profileService.update(form);
      setSuccess('Profile saved');
    } catch (err) {
      setSaveError(err?.message || 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="header-row">
        <div>
          <h1 className="h1">Profile</h1>
          <div className="p-muted">Edit your profile information</div>
        </div>
        <div>
          <Button onClick={save} disabled={saving}>{saving ? 'Saving...' : 'Save'}</Button>
        </div>
      </div>

      <Card>
        {loading ? <div>Loading...</div> : error ? <div role="alert">Unable to load profile</div> : (
          <form onSubmit={save}>
            <div className="form-row">
              <div className="form-col">
                <Input id="first_name" label="First name" value={form.first_name || ''} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
              </div>
              <div className="form-col">
                <Input id="last_name" label="Last name" value={form.last_name || ''} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
              </div>
            </div>

            <Input id="headline" label="Headline" value={form.headline || ''} onChange={(e) => setForm({ ...form, headline: e.target.value })} />
            <div style={{ marginBottom: 12 }}>
              <label className="small">About</label>
              <textarea className="input" rows="6" value={form.about || ''} onChange={(e) => setForm({ ...form, about: e.target.value })} />
            </div>

            <div style={{ marginBottom: 12 }}>
              <label className="small">Skills (comma separated)</label>
              <input className="input" value={(form.skills || []).join(', ')} onChange={(e) => setForm({ ...form, skills: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })} />
            </div>

            {saveError && <div role="alert" style={{ color: '#d14343' }}>{saveError}</div>}
            {success && <div role="status" style={{ color: 'green' }}>{success}</div>}

            <div style={{ display: 'flex', gap: 8 }}>
              <Button type="submit" disabled={saving}>{saving ? 'Saving...' : 'Save changes'}</Button>
              <button type="button" className="btn ghost" onClick={() => window.location.reload()}>Reset</button>
            </div>
          </form>
        )}
      </Card>
    </div>
  );
}
