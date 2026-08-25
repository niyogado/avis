import api from './api';

export const applicationsService = {
  list: async (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return api.get(`/applications${qs ? `?${qs}` : ''}`);
  },
  get: async (id) => api.get(`/applications/${id}`),
  withdraw: async (id) => api.post(`/applications/${id}/withdraw`, {}),
};
