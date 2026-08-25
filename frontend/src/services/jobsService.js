import api from './api';

export const jobsService = {
  list: async (params = {}) => {
    // simple query string builder
    const qs = new URLSearchParams(params).toString();
    return api.get(`/jobs${qs ? `?${qs}` : ''}`);
  },
  get: async (id) => api.get(`/jobs/${id}`),
  apply: async (id) => api.post(`/jobs/${id}/apply`, {}),
  save: async (id) => api.post(`/jobs/${id}/save`, {}),
};
