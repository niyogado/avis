import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import CanvasBackground from '../components/CanvasBackground'

export default function Register() {
  const { register } = useAuth()

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    username: '',
    email: '',
    phone: '',
    password: '',
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    const payload = {
      ...formData,
      phone: formData.phone.trim().replace(/\.$/, ''),
    }

    try {
      await register(payload)
    } catch (err) {
      // Handles standard string details or FastAPI array validation errors
      const detail = err?.response?.data?.detail
      if (Array.isArray(detail)) {
        setError(detail.map((e) => e.msg).join(', '))
      } else {
        setError(detail || 'Registration failed')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center">
      <CanvasBackground />
      <div className="relative z-10 w-full max-w-md p-4">
        <div className="panel p-6 rounded bg-[#191915] text-[#F3F1E9] border border-[rgba(243,241,233,0.12)]">
          <h2 className="text-xl font-semibold mb-4">Create your AVIS account</h2>

          {error && (
            <div className="p-3 mb-4 rounded bg-[rgba(217,106,28,0.15)] text-[#D96A1C] text-sm border border-[rgba(217,106,28,0.3)]">
              {error}
            </div>
          )}

          <form onSubmit={submit} className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm block mb-1">First Name</label>
                <input
                  name="first_name"
                  type="text"
                  required
                  className="w-full p-2 rounded bg-[#0E0E0C] border border-[rgba(243,241,233,0.12)] text-[#F3F1E9] focus:border-[#D96A1C] outline-none"
                  value={formData.first_name}
                  onChange={handleChange}
                />
              </div>
              <div>
                <label className="text-sm block mb-1">Last Name</label>
                <input
                  name="last_name"
                  type="text"
                  required
                  className="w-full p-2 rounded bg-[#0E0E0C] border border-[rgba(243,241,233,0.12)] text-[#F3F1E9] focus:border-[#D96A1C] outline-none"
                  value={formData.last_name}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div>
              <label className="text-sm block mb-1">Username</label>
              <input
                name="username"
                type="text"
                required
                className="w-full p-2 rounded bg-[#0E0E0C] border border-[rgba(243,241,233,0.12)] text-[#F3F1E9] focus:border-[#D96A1C] outline-none"
                value={formData.username}
                onChange={handleChange}
              />
            </div>

            <div>
              <label className="text-sm block mb-1">Email</label>
              <input
                name="email"
                type="email"
                required
                className="w-full p-2 rounded bg-[#0E0E0C] border border-[rgba(243,241,233,0.12)] text-[#F3F1E9] focus:border-[#D96A1C] outline-none"
                value={formData.email}
                onChange={handleChange}
              />
            </div>

            <div>
              <label className="text-sm block mb-1">Phone</label>
              <input
                name="phone"
                type="tel"
                required
                className="w-full p-2 rounded bg-[#0E0E0C] border border-[rgba(243,241,233,0.12)] text-[#F3F1E9] focus:border-[#D96A1C] outline-none"
                value={formData.phone}
                onChange={handleChange}
              />
            </div>

            <div>
              <label className="text-sm block mb-1">Password</label>
              <input
                name="password"
                type="password"
                required
                className="w-full p-2 rounded bg-[#0E0E0C] border border-[rgba(243,241,233,0.12)] text-[#F3F1E9] focus:border-[#D96A1C] outline-none"
                value={formData.password}
                onChange={handleChange}
              />
            </div>

            <div className="flex items-center justify-between pt-2">
              <button
                type="submit"
                className="px-4 py-2 bg-[#D96A1C] hover:bg-opacity-90 text-white font-medium rounded disabled:opacity-50 transition-colors"
                disabled={loading}
              >
                {loading ? 'Creating...' : 'Create account'}
              </button>
              <Link to="/login" className="text-sm text-[rgba(243,241,233,0.6)] hover:text-[#F3F1E9]">
                Sign in
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}