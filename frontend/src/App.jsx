import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Overview from './views/Overview'
import Profile from './views/Profile'
import MyCV from './views/MyCV'
import Login from './views/Login'
import Register from './views/Register'
import { AuthProvider } from './contexts/AuthContext'

export default function App() {
  return (
    <AuthProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/cv" element={<MyCV />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </AuthProvider>
  )
}
