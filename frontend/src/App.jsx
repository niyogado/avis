import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Overview from './views/Overview'
import Profile from './views/Profile'
import Identity from './views/Identity'
import MyCV from './views/MyCV'
import CVWriter from './views/CVWriter'
import Training from './views/Training'
import Chat from './views/Chat'
import CareerHub from './views/CareerHub'
import Settings from './views/Settings'
import Login from './views/Login'
import Register from './views/Register'
import CareerIntelligence from './views/CareerIntelligence'
import Learning from './views/Learning'
import Knowledge from './views/Knowledge'
import { AuthProvider } from './contexts/AuthContext'

export default function App() {
  return (
    <AuthProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/identity" element={<Identity />} />
          <Route path="/cv" element={<MyCV />} />
          <Route path="/cv-writer" element={<CVWriter />} />
          <Route path="/training" element={<Training />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/career/intelligence" element={<CareerIntelligence />} />
          <Route path="/career" element={<CareerHub />} />
          <Route path="/knowledge" element={<Knowledge />} />
          <Route path="/learning" element={<Learning />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          {/* Legacy Career Hub paths — redirect into the unified /career hub. */}
          <Route path="/opportunities" element={<Navigate to="/career" replace />} />
          <Route path="/career/applications" element={<Navigate to="/career" replace />} />
          <Route path="/job-alerts" element={<Navigate to="/career" replace />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </AuthProvider>
  )
}
