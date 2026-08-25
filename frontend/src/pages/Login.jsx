import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate, Link } from 'react-router-dom';
import { Input } from '../components/Input';
import { Button } from '../components/Button';
import { Icon } from '../components/Icons';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(form);
      navigate('/dashboard');
    } catch (err) {
      setError(err?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const oauthProviders = [
    { id: 'google', label: 'Continue with Google', icon: 'google' },
    { id: 'microsoft', label: 'Continue with Microsoft', icon: 'microsoft' },
    { id: 'apple', label: 'Continue with Apple', icon: 'apple' },
    { id: 'linkedin', label: 'Continue with LinkedIn', icon: 'linkedin' },
  ];

  const startOAuth = (provider) => {
    // Redirect to backend OAuth start endpoint. Backend must implement provider redirect.
    const base = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
    const url = `${base}/auth/oauth/${provider}`;
    // Open in same tab to allow callback to return to /oauth/callback
    window.location.href = url;
  };

  return (
    <div className="content" style={{ maxWidth: 520 }}>
      <div className="card">
        <h2 className="h1">Sign in to AVIS</h2>
        <p className="p-muted">Access your CV, training and job matches</p>

        <div style={{ display: 'grid', gap: 8, marginTop: 12 }}>
          {oauthProviders.map((p) => (
            <button
              key={p.id}
              className="btn ghost"
              onClick={() => startOAuth(p.id)}
              style={{ display: 'flex', alignItems: 'center', gap: 10 }}
              aria-label={p.label}
            >
              <Icon name={p.icon} size={18} />
              <span style={{ flex: 1, textAlign: 'left' }}>{p.label}</span>
            </button>
          ))}
        </div>

        <div style={{ height: 1, background: 'rgba(0,0,0,0.04)', margin: '16px 0' }} />

        <form onSubmit={submit} aria-label="Login form">
          <Input
            id="email"
            label="Email"
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
          />
          <Input
            id="password"
            label="Password"
            type="password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            required
          />

          {error && <div role="alert" style={{ color: '#d14343', marginBottom: 12 }}>{error}</div>}

          <div style={{ display: 'flex', gap: 8 }}>
            <Button type="submit" disabled={loading}>{loading ? 'Signing in...' : 'Sign in'}</Button>
            <Link to="/register" className="btn ghost" style={{ alignSelf: 'center', textDecoration: 'none' }}>Create account</Link>
          </div>
        </form>

        <div style={{ marginTop: 12 }} className="small">
          <Link to="/forgot" style={{ color: 'var(--muted)' }}>Forgot password?</Link>
        </div>
      </div>
    </div>
  );
}
