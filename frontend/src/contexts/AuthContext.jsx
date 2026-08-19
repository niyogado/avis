import React, { createContext, useContext, useEffect, useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem('user') || 'null'))
  const navigate = useNavigate()

  useEffect(() => {
    if (token) localStorage.setItem('token', token)
    else localStorage.removeItem('token')
  }, [token])

  useEffect(() => {
    if (user) localStorage.setItem('user', JSON.stringify(user))
    else localStorage.removeItem('user')
  }, [user])

  const fetchProfile = async (accessToken) => {
    try {
      const profileRes = await axios.get('http://localhost:8000/api/profile/', {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      setUser(profileRes.data)
      return profileRes.data
    } catch (_) {
      setUser(null)
      return null
    }
  }

  const login = async ({ email, password }) => {
    // Backend expects exact JSON keys: { "email": "...", "password": "..." }
    const res = await axios.post(
      'http://localhost:8000/api/auth/login',
      { email, password },
      { headers: { 'Content-Type': 'application/json' } }
    )

    const access = res.data.access_token
    setToken(access)

    await fetchProfile(access)

    navigate('/')
    return res.data
  }

  const register = async (userData) => {
    // 1. Register
    const regRes = await axios.post(
      'http://localhost:8000/api/auth/register',
      userData,
      { headers: { 'Content-Type': 'application/json' } }
    )

    // 2. Login automatically using exact email field
    const loginRes = await axios.post(
      'http://localhost:8000/api/auth/login',
      { email: userData.email, password: userData.password },
      { headers: { 'Content-Type': 'application/json' } }
    )

    const access = loginRes.data.access_token
    setToken(access)

    // 3. Update/Create profile info
    const profilePayload = {
      first_name: userData.first_name || '',
      last_name: userData.last_name || '',
      phone: userData.phone || '',
      headline: '',
      summary: '',
    }

    try {
      const profileRes = await axios.post('http://localhost:8000/api/profile/', profilePayload, {
        headers: { Authorization: `Bearer ${access}` },
      })
      setUser(profileRes.data)
    } catch (err) {
      try {
        const profilePutRes = await axios.put('http://localhost:8000/api/profile/', profilePayload, {
          headers: { Authorization: `Bearer ${access}` },
        })
        setUser(profilePutRes.data)
      } catch (_) {
        setUser(null)
      }
    }

    navigate('/')
    return regRes.data
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    navigate('/login')
  }

  return (
    <AuthContext.Provider value={{ token, user, setUser, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}