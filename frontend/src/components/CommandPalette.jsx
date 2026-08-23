import React, { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowUpRight, Bell, BookOpen, Brain, Compass, FileText, GraduationCap, MessageCircle, Search, Send, Sparkles, Target } from 'lucide-react'

const commands = [
  { label: 'Search knowledge', icon: Search, path: '/identity' },
  { label: 'Start training', icon: GraduationCap, path: '/training' },
  { label: 'Upload CV', icon: FileText, path: '/cv' },
  { label: 'Open Chat', icon: MessageCircle, path: '/chat' },
  { label: 'Find opportunities', icon: Compass, path: '/career' },
  { label: 'Create CV', icon: Sparkles, path: '/cv-writer' },
  { label: 'View applications', icon: Send, path: '/career' },
  { label: 'Review learning', icon: BookOpen, path: '/learning' },
]

export default function CommandPalette({ open, onClose }) {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')

  useEffect(() => {
    if (!open) return
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') onClose()
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [open, onClose])

  const filteredCommands = useMemo(() => {
    const term = query.trim().toLowerCase()
    if (!term) return commands
    return commands.filter((command) => command.label.toLowerCase().includes(term))
  }, [query])

  if (!open) return null

  return (
    <div className="command-overlay" onClick={onClose}>
      <div className="command-panel" onClick={(event) => event.stopPropagation()} role="dialog" aria-modal="true">
        <div className="command-search">
          <Search size={16} />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search actions, knowledge, CV, career..."
            autoFocus
          />
        </div>

        <div className="command-list">
          {filteredCommands.length > 0 ? (
            filteredCommands.map(({ label, icon: Icon, path }) => (
              <button
                type="button"
                key={label}
                className="command-item"
                onClick={() => {
                  navigate(path)
                  onClose()
                }}
              >
                <span className="command-icon"><Icon size={16} /></span>
                <span>{label}</span>
                <ArrowUpRight size={14} />
              </button>
            ))
          ) : (
            <div className="command-empty">No matching actions.</div>
          )}
        </div>
      </div>
    </div>
  )
}
