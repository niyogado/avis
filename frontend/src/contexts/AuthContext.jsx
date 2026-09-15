import React, { createContext, useContext, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import apiClient from '../api/config'

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
      const profileRes = await apiClient.get('/api/profile/', {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      setUser(profileRes.data)
      return profileRes.data
    } catch (error) {
      if (error.response?.status === 404) {
        const fallbackName = [user?.first_name, user?.last_name].filter(Boolean).join(' ') || 'New user'
        const fallbackProfile = {
          first_name: user?.first_name || '',
          last_name: user?.last_name || '',
          full_name: fallbackName,
          headline: '',
          summary: '',
          location: '',
          phone: user?.phone || '',
          avatar_url: '',
        }

        try {
          const created = await apiClient.put('/api/profile/', fallbackProfile, {
            headers: { Authorization: `Bearer ${accessToken}` },
          })
          setUser(created.data)
          return created.data
        } catch (_) {
          setUser(null)
          return null
        }
      }

      setUser(null)
      return null
    }
  }

  const login = async ({ email, password }) => {
    const res = await apiClient.post('/api/auth/login', { email, password })
    const access = res.data.access_token
    setToken(access)

    const profile = await fetchProfile(access)
    if (profile) {
      navigate('/')
    }
    return res.data
  }

  const register = async (userData) => {
    const regRes = await apiClient.post('/api/auth/register', userData)

    const loginRes = await apiClient.post('/api/auth/login', {
      email: userData.email,
      password: userData.password,
    })

    const access = loginRes.data.access_token
    setToken(access)

    const profile = await fetchProfile(access)
    if (profile) {
      navigate('/')
    }
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