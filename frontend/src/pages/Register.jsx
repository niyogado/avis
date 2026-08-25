import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate, Link } from 'react-router-dom';
import { Input } from '../components/Input';
import { Button } from '../components/Button';
import { Icon } from '../components/Icons';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register(form);
      navigate('/dashboard');
    } catch (err) {
      setError(err?.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const oauthProviders = [
    { id: 'google', label: 'Sign up with Google', icon: 'google' },
    { id: 'microsoft', label: 'Sign up with Microsoft', icon: 'microsoft' },
    { id: 'apple', label: 'Sign up with Apple', icon: 'apple' },
    { id: 'linkedin', label: 'Sign up with LinkedIn', icon: 'linkedin' },
  ];

  const startOAuth = (provider) => {
    const base = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
    window.location.href = `${base}/auth/oauth/${provider}`;
  };

  return (
    <div className="content" style={{ maxWidth: 720 }}>
      <div className="card">
        <h2 className="h1">Create an account</h2>
        <p className="p-muted">Join AVIS to start building your career</p>

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

        <form onSubmit={submit} aria-label="Register form">
          <div className="form-row">
            <div className="form-col">
              <Input id="first_name" label="First name" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} required />
            </div>
            <div className="form-col">
              <Input id="last_name" label="Last name" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} required />
            </div>
          </div>

          <Input id="email" label="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          <Input id="password" label="Password" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />

          {error && <div role="alert" style={{ color: '#d14343', marginBottom: 12 }}>{error}</div>}

          <div style={{ display: 'flex', gap: 8 }}>
            <Button type="submit" disabled={loading}>{loading ? 'Creating...' : 'Create account'}</Button>
            <Link to="/login" className="btn ghost" style={{ alignSelf: 'center', textDecoration: 'none' }}>Sign in</Link>
          </div>
        </form>
      </div>
    </div>
  );
}
