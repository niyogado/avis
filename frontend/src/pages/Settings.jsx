import React, { useState, useEffect } from 'react';
import { Card } from '../components/Card';
import { useTheme } from '../components/ThemeProvider';
import { Button } from '../components/Button';

export default function Settings() {
  const { theme, toggle } = useTheme();
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  const save = async () => {
    setSaving(true);
    setMessage(null);
    try {
      // If backend settings endpoint exists, call it here.
      setMessage('Settings saved');
    } catch (err) {
      setMessage('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="header-row">
        <div>
          <h1 className="h1">Settings</h1>
          <div className="p-muted">Manage account and preferences</div>
        </div>
      </div>

      <Card>
        <div style={{ display: 'grid', gap: 12 }}>
          <div>
            <div className="small">Theme</div>
            <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
              <Button onClick={toggle} className="ghost">{theme === 'dark' ? 'Switch to Light' : 'Switch to Dark'}</Button>
            </div>
          </div>

          <div>
            <div className="small">Danger zone</div>
            <div style={{ marginTop: 8 }}>
              <button className="btn ghost" onClick={() => alert('Delete account flow not implemented in frontend-only demo')}>Delete account</button>
            </div>
          </div>

          {message && <div role="status">{message}</div>}

          <div style={{ display: 'flex', gap: 8 }}>
            <Button onClick={save} disabled={saving}>{saving ? 'Saving...' : 'Save settings'}</Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
