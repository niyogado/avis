import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Header(){
  const { user } = useAuth()

  const initials = React.useMemo(()=>{
    if(!user) return 'U'
    if(user.full_name) return user.full_name.split(' ').map(n=>n[0]).slice(0,2).join('').toUpperCase()
    if(user.email) return user.email[0].toUpperCase()
    return 'U'
  },[user])

  return (
    <header className="flex items-center justify-between pb-3 border-b" style={{ borderColor: 'rgba(243,241,233,0.04)' }}>
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-semibold">AVIS</h1>
        <div className="text-sm text-[rgba(243,241,233,0.6)]">Overview</div>
      </div>

      <div>
        {user ? (
          <Link to="/profile" className="flex items-center gap-3">
            <div className="text-right mr-2 hidden sm:block">
              <div className="text-sm text-[#F3F1E9]">{user.full_name}</div>
              <div className="text-xs text-[rgba(243,241,233,0.6)]">{user.email}</div>
            </div>
            {user.avatar_url ? (
              <img src={user.avatar_url} alt="avatar" className="w-9 h-9 rounded-full object-cover" />
            ) : (
              <div className="w-9 h-9 rounded-full bg-[#D96A1C] flex items-center justify-center text-white font-semibold">{initials}</div>
            )}
          </Link>
        ) : (
          <Link to="/login" className="px-3 py-1 text-[rgba(243,241,233,0.8)] rounded">Sign in</Link>
        )}
      </div>
    </header>
  )
}
