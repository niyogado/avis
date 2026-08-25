import api from './api';

export const profileService = {
  get: async () => api.get('/profile'),
  update: async (payload) => api.put('/profile', payload),
};
