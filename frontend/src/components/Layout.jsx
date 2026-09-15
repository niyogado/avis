import React from 'react'
import { useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

const AUTH_PATHS = ['/login', '/register', '/signup']

export default function Layout({ children }) {
  const { pathname } = useLocation()
  const isAuth = AUTH_PATHS.includes(pathname)

  return (
    <div className="app-shell">
      {!isAuth && (
        <aside className="sidebar-panel">
          <Sidebar />
        </aside>
      )}

      <main className={`app-main ${isAuth ? 'auth-main' : ''}`}>
        {!isAuth && <Header />}
        <div className="page-content">{children}</div>
      </main>
    </div>
  )
}
