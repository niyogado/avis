import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { Bell, Brain, Command, Search, Sparkles } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import CommandPalette from './CommandPalette'

export default function Header() {
  const { user } = useAuth()
  const [paletteOpen, setPaletteOpen] = useState(false)

  const initials = React.useMemo(() => {
    if (!user) return 'U'
    if (user.full_name) return user.full_name.split(' ').map((n) => n[0]).slice(0, 2).join('').toUpperCase()
    if (user.email) return user.email[0].toUpperCase()
    return 'U'
  }, [user])

  React.useEffect(() => {
    const handleKeyDown = (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        setPaletteOpen(true)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <>
      <header className="topbar">
        <div className="brand-block">
          <span className="brand-word">AVIS</span>
        </div>

        <div className="topbar-actions">
          <button type="button" className="command-trigger" onClick={() => setPaletteOpen(true)}>
            <Search size={15} />
            <span>Search</span>
            <span className="shortcut">⌘K</span>
          </button>

          <div className="status-pill">
            <Brain size={12} />
            <span>{user ? "Ai Active": "Ai inactive"}</span>
          </div>

          <button type="button" className="icon-button" aria-label="Notifications">
            <Bell size={16} />
          </button>

          {user ? (
            <>
              <Link to="/" className="text-button small">Dashboard</Link>
              <Link to="/profile" className="avatar-wrap" aria-label="Profile">
                {user.avatar_url ? (
                  <img src={user.avatar_url} alt="avatar" className="user-avatar" />
                ) : (
                  <div className="user-avatar initials">{initials}</div>
                )}
              </Link>
            </>
          ) : (
            <Link to="/login" className="text-button small">
              Sign in
            </Link>
          )}
        </div>
      </header>

      <CommandPalette open={paletteOpen} onClose={() => setPaletteOpen(false)} />
    </>
  )
}
