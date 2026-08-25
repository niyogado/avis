import React, { useEffect, useState } from 'react';
import { cvService } from '../services/cvService';
import { Card } from '../components/Card';
import { Button } from '../components/Button';

export default function CVWriter() {
  const [cv, setCv] = useState({ summary: '', experience: '', education: '', skills: '' });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const data = await cvService.get();
        if (!mounted) return;
        setCv({
          summary: data?.summary || '',
          experience: data?.experience || '',
          education: data?.education || '',
          skills: (data?.skills || []).join(', '),
        });
      } catch {
        // ignore
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => (mounted = false);
  }, []);

  const save = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const payload = {
        summary: cv.summary,
        experience: cv.experience,
        education: cv.education,
        skills: cv.skills.split(',').map(s => s.trim()).filter(Boolean),
      };
      await cvService.save(payload);
      setMessage('CV saved');
    } catch (err) {
      setMessage(err?.message || 'Save failed');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="header-row">
        <div>
          <h1 className="h1">CV Writer</h1>
          <div className="p-muted">Edit and export your CV</div>
        </div>
        <div>
          <Button onClick={save} disabled={saving}>{saving ? 'Saving...' : 'Save'}</Button>
        </div>
      </div>

      <Card>
        {loading ? <div>Loading...</div> : (
          <form onSubmit={(e) => { e.preventDefault(); save(); }}>
            <div style={{ marginBottom: 12 }}>
              <label className="small">Professional summary</label>
              <textarea className="input" rows="4" value={cv.summary} onChange={(e) => setCv({ ...cv, summary: e.target.value })} />
            </div>

            <div style={{ marginBottom: 12 }}>
              <label className="small">Experience</label>
              <textarea className="input" rows="6" value={cv.experience} onChange={(e) => setCv({ ...cv, experience: e.target.value })} />
            </div>

            <div style={{ marginBottom: 12 }}>
              <label className="small">Education</label>
              <textarea className="input" rows="4" value={cv.education} onChange={(e) => setCv({ ...cv, education: e.target.value })} />
            </div>

            <div style={{ marginBottom: 12 }}>
              <label className="small">Skills (comma separated)</label>
              <input className="input" value={cv.skills} onChange={(e) => setCv({ ...cv, skills: e.target.value })} />
            </div>

            {message && <div role="status" style={{ marginBottom: 12 }}>{message}</div>}

            <div style={{ display: 'flex', gap: 8 }}>
              <Button type="button" onClick={save} disabled={saving}>{saving ? 'Saving...' : 'Save CV'}</Button>
            </div>
          </form>
        )}
      </Card>
    </div>
  );
}
