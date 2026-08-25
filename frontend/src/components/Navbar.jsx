import React from 'react';
import { useTheme } from './ThemeProvider';
import { useAuth } from '../hooks/useAuth';

export function Navbar() {
  const { toggle, theme } = useTheme();
  const { user } = useAuth();

  return (
    <header className="navbar" role="banner">
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <button className="btn ghost" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
          Home
        </button>
        <div className="small p-muted">Welcome back{user?.first_name ? `, ${user.first_name}` : ''}</div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <button
          className="btn ghost"
          onClick={toggle}
          aria-pressed={theme === 'dark'}
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? 'Light' : 'Dark'}
        </button>
      </div>
    </header>
  );
}
