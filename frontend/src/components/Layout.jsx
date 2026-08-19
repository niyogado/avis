import React from 'react'
import { useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

const AUTH_PATHS = ['/login', '/register', '/signup']

export default function Layout({ children }) {
  const { pathname } = useLocation()
  const isAuth = AUTH_PATHS.includes(pathname)

  return (
    <div className="flex h-screen">
      {!isAuth && (
        <aside className="sidebar fixed h-full" style={{ width: 260 }}>
          <Sidebar />
        </aside>
      )}

      <main className="flex-1 p-6 flex flex-col" style={{ background: '#0E0E0C', marginLeft: isAuth ? 0 : 260 }}>
        <Header />
        <div className="mt-4 flex-1 overflow-auto">{children}</div>
      </main>
    </div>
  )
}
