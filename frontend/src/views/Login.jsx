import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import CanvasBackground from '../components/CanvasBackground'

export default function Login() {
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      await login({ email, password })
    } catch (err) {
      const detail = err?.response?.data?.detail
      if (Array.isArray(detail)) {
        setError(detail.map((e) => e.msg).join(', '))
      } else {
        setError(detail || 'Invalid email or password')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative h-screen w-screen overflow-hidden flex items-center justify-center p-4 bg-[#0E0E0C]">
      <CanvasBackground />
      <div className="relative z-10 w-full max-w-md">
        <div className="panel p-6 sm:p-8 rounded-2xl bg-[#191915]/80 backdrop-blur-md border border-[rgba(243,241,233,0.12)] shadow-2xl text-[#F3F1E9]">
          <div className="mb-5 text-center">
            <h2 className="text-2xl font-bold tracking-tight">Welcome Back</h2>
            <p className="text-xs text-[rgba(243,241,233,0.6)] mt-1">
              Sign in to continue to AVIS
            </p>
          </div>

          {error && (
            <div className="p-3 mb-4 rounded-xl bg-[rgba(217,106,28,0.12)] text-[#D96A1C] text-xs border border-[rgba(217,106,28,0.25)] font-medium">
              {error}
            </div>
          )}

          <form onSubmit={submit} className="space-y-3.5">
            <div className="space-y-1">
              <label className="text-xs font-medium text-[rgba(243,241,233,0.7)]">Email Address</label>
              <input
                type="email"
                required
                placeholder="jane@example.com"
                className="w-full px-3.5 py-2 rounded-xl bg-[#0E0E0C] border border-[rgba(243,241,233,0.12)] text-[#F3F1E9] placeholder-[rgba(243,241,233,0.2)] focus:border-[#D96A1C] focus:ring-1 focus:ring-[#D96A1C] outline-none transition-all text-sm"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-[rgba(243,241,233,0.7)]">Password</label>
              <input
                type="password"
                required
                placeholder="••••••••"
                className="w-full px-3.5 py-2 rounded-xl bg-[#0E0E0C] border border-[rgba(243,241,233,0.12)] text-[#F3F1E9] placeholder-[rgba(243,241,233,0.2)] focus:border-[#D96A1C] focus:ring-1 focus:ring-[#D96A1C] outline-none transition-all text-sm"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-2.5 px-4 bg-[#D96A1C] hover:bg-[#c25e17] active:scale-[0.99] text-white text-sm font-semibold rounded-xl shadow-lg shadow-[#D96A1C]/20 disabled:opacity-50 transition-all duration-150"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <p className="mt-5 text-center text-xs text-[rgba(243,241,233,0.6)]">
            Don't have an account?{' '}
            <Link to="/register" className="text-[#D96A1C] hover:underline font-medium">
              Create account
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}