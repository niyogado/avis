import api from './api';

export const trainingService = {
  list: async (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return api.get(`/training${qs ? `?${qs}` : ''}`);
  },
  get: async (id) => api.get(`/training/${id}`),
  complete: async (id) => api.post(`/training/${id}/complete`, {}),
};
