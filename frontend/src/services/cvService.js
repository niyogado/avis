import api from './api';

export const cvService = {
  get: async () => api.get('/cv'),
  evaluate: async (fileData) => {
    // If backend expects multipart
    if (fileData instanceof FormData) {
      return api.post('/cv/evaluate', fileData, false);
    }
    return api.post('/cv/evaluate', fileData);
  },
  save: async (payload) => api.put('/cv', payload),
  export: async (format = 'pdf') => api.post('/cv/export', { format }),
};
