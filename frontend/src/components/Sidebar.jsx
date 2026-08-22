import React from 'react'
import { NavLink, Link } from 'react-router-dom'
import { Bell, BookOpen, Brain, BriefcaseBusiness, Compass, FileText, Fingerprint, GraduationCap, LayoutDashboard, MessageCircle, PenLine, Send, Settings as SettingsIcon, User } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const navItems = [
  { label: 'Overview', path: '/', icon: LayoutDashboard },
  { label: 'Identity', path: '/identity', icon: Fingerprint },
  { label: 'CV', path: '/cv', icon: FileText },
  { label: 'Training', path: '/training', icon: GraduationCap },
  { label: 'Knowledge', path: '/knowledge', icon: Brain },
  { label: 'Chat', path: '/chat', icon: MessageCircle },
  { label: 'CV Writer', path: '/cv-writer', icon: PenLine },
  { label: 'Career Intelligence', path: '/career/intelligence', icon: Compass },
  { label: 'Opportunities', path: '/opportunities', icon: BriefcaseBusiness },
  { label: 'Applications', path: '/career/applications', icon: Send },
  { label: 'Job Alerts', path: '/job-alerts', icon: Bell },
  { label: 'Learning', path: '/learning', icon: BookOpen },
  { label: 'Settings', path: '/settings', icon: SettingsIcon },
]

export default function Sidebar() {
  const { user, logout } = useAuth()

  return (
    <div className="sidebar-shell">
      <div className="nav-group">
        <nav className="nav-list">
          {navItems.map(({ label, path, icon: Icon }) => (
            <NavLink
              key={label}
              to={path}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <span className="nav-icon"><Icon size={16} /></span>
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
      </div>

      <div className="sidebar-footer">
        {user ? (
          <>
            <Link to="/" className="profile-link">
              <span className="nav-icon"><LayoutDashboard size={16} /></span>
              <span>Dashboard</span>
            </Link>
            <Link to="/profile" className="profile-link">
              <span className="nav-icon"><User size={16} /></span>
              <span>{user.full_name || user.email || 'Profile'}</span>
            </Link>
            <button type="button" onClick={logout} className="logout-button">Logout</button>
          </>
        ) : (
          <div className="auth-links">
            <Link to="/login">Sign in</Link>
            <Link to="/register">Create account</Link>
          </div>
        )}
      </div>
    </div>
  )
}