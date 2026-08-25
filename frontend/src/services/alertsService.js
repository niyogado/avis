import api from './api';

export const alertsService = {
  list: async () => api.get('/alerts'),
  create: async (payload) => api.post('/alerts', payload),
  update: async (id, payload) => api.put(`/alerts/${id}`, payload),
  delete: async (id) => api.del(`/alerts/${id}`),
};
