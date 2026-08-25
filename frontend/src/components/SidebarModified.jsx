import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import logo from '../assets/dove-logo.svg';
import { Icon } from './Icons';

export function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const links = [
    { to: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
    { to: '/profile', label: 'Profile', icon: 'profile' },
    { to: '/cv', label: 'CV', icon: 'cv' },
    { to: '/cv-writer', label: 'CV Writer', icon: 'cv' },
    { to: '/jobs', label: 'Jobs', icon: 'jobs' },
    { to: '/applications', label: 'Applications', icon: 'alerts' },
    { to: '/training', label: 'Training', icon: 'cv' },
    { to: '/chat', label: 'Chat', icon: 'chat' },
    { to: '/alerts', label: 'Job Alerts', icon: 'alerts' },
    { to: '/settings', label: 'Settings', icon: 'profile' },
  ];

  return (
    <aside className="sidebar" aria-label="Main navigation">
      <div className="brand" role="banner">
        <img src={logo} alt="AVIS logo" />
        <div>
          <div style={{ fontWeight: 800 }}>AVIS</div>
          <div className="small">Youth Careers</div>
        </div>
      </div>

      <nav aria-label="Primary">
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            aria-current={undefined}
          >
            <Icon name={l.icon} size={18} />
            <span className="label">{l.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="footer">
        <div className="small">Signed in as</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div className="avatar" aria-hidden>
            {user?.first_name ? user.first_name[0] : 'U'}
          </div>
          <div>
            <div style={{ fontWeight: 700 }}>{user?.first_name || 'Guest'}</div>
            <div className="small">{user?.email || ''}</div>
          </div>
        </div>

        <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
          <button className="btn ghost" onClick={() => navigate('/profile')} aria-label="Edit profile">
            <Icon name="profile" />
            <span style={{ marginLeft: 8 }}>Edit</span>
          </button>
          <button className="btn" onClick={() => logout()} aria-label="Logout">
            <Icon name="logout" />
            <span style={{ marginLeft: 8 }}>Logout</span>
          </button>
        </div>
      </div>
    </aside>
  );
}
