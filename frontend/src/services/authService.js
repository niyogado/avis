import api from './api';

export const authService = {
  login: async ({ email, password }) => {
    const data = await api.post('/auth/login', { email, password });
    // Expect { access_token, token_type, user }
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
      // ignore
    } finally {
      localStorage.removeItem('avis_token');
    }
  },
  me: async () => {
    return api.get('/auth/me');
  },
};
