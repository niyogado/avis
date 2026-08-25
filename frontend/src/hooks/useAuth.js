import React, { createContext, useContext, useEffect, useState } from 'react';
import { authService } from '../services/authService';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loadingAuth, setLoadingAuth] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const me = await authService.me();
        if (mounted) setUser(me);
      } catch {
        setUser(null);
      } finally {
        if (mounted) setLoadingAuth(false);
      }
    }
    load();
    return () => (mounted = false);
  }, []);

  const login = async (creds) => {
    const res = await authService.login(creds);
    if (res?.access_token) {
      const me = await authService.me();
      setUser(me);
      return me;
    }
    return null;
  };

  const register = async (payload) => {
    const res = await authService.register(payload);
    if (res?.access_token) {
      const me = await authService.me();
      setUser(me);
      return me;
    }
    return null;
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
    navigate('/login');
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loadingAuth }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
