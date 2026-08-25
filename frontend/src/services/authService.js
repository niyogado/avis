import api from './api';

export const authService = {
  login: async ({ email, password }) => {
    const data = await api.post('/auth/login', { email, password });
    if (data?.access_token) {
      localStorage.setItem('avis_token', data.access_token);
    }
    return data;
  },
  register: async (payload) => {
    const data = await api.post('/auth/register', payload);
    if (data?.access_token) {
      localStorage.setItem('avis_token', data.access_token);
    }
    return data;
  },
  logout: async () => {
    try {
      await api.post('/auth/logout', {});
    } catch {
      // ignore backend errors on logout
    } finally {
      localStorage.removeItem('avis_token');
    }
  },
  me: async () => {
    return api.get('/auth/me');
  },

  /**
   * OAuth helpers
   *
   * startOAuthUrl(provider) returns the backend URL to start OAuth flow.
   * The backend must implement a route that redirects to the provider's auth page.
   */
  startOAuthUrl: (provider) => {
    const base = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
    return `${base}/auth/oauth/${provider}`;
  },

  /**
   * exchangeOAuthCode(provider, code)
   * Attempts to exchange an authorization code with the backend.
   * Backend must implement /auth/oauth/callback?provider=... to accept POST { code } and return access_token.
   */
  exchangeOAuthCode: async (provider, code) => {
    return api.post(`/auth/oauth/callback?provider=${encodeURIComponent(provider)}`, { code });
  },
};
