import React from 'react'
import { NavLink, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

// Explicitly map label to actual React Router paths
const navItems = [
  { label: 'Overview', path: '/' },
  { label: 'My Profile', path: '/profile' },
  { label: 'My CV', path: '/cv' },
  { label: 'CV Writer', path: '/cv-writer' },
  { label: 'Training', path: '/training' },
  { label: 'Chat', path: '/chat' },
  { label: 'Career Applications', path: '/career-applications' },
  { label: 'Job Alerts', path: '/job-alerts' },
  { label: 'Settings', path: '/settings' },
]

export default function Sidebar() {
  const { user, logout } = useAuth()

  return (
    <div className="p-6 flex flex-col h-full justify-between">
      <div>
        <h2 className="text-2xl font-bold mb-6">AVIS</h2>
        <nav className="flex flex-col gap-2">
          {navItems.map((item) => (
            <NavLink
              key={item.label}
              to={item.path}
              className={({ isActive }) =>
                `block px-3 py-2 rounded transition-colors ${
                  isActive ? 'bg-[#D96A1C] text-white' : 'hover:bg-[rgba(243,241,233,0.05)]'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </div>

      <div className="text-sm">
        <div className="mb-3 flex items-center gap-2">
          <button className="px-3 py-2 rounded bg-[#D96A1C] text-white">Dark</button>
        </div>

        {user ? (
          <div className="text-xs text-[#F3F1E9]">
            <Link to="/profile" className="block font-medium hover:underline mb-1">
              {user.full_name || `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.email || 'You'}
            </Link>
            <button 
              onClick={logout} 
              className="mt-1 text-sm text-[rgba(243,241,233,0.6)] hover:text-white transition-colors"
            >
              Logout
            </button>
          </div>
        ) : (
          <div className="text-xs text-[#F3F1E9]">
            <Link to="/login" className="block mb-1 text-[rgba(243,241,233,0.8)] hover:text-white">
              Sign in
            </Link>
            <Link to="/register" className="block text-[rgba(243,241,233,0.6)] hover:text-white">
              Create account
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}