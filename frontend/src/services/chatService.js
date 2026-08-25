import api from './api';

export const chatService = {
  sendMessage: async (message) => api.post('/chat', { message }),
  history: async () => api.get('/chat/history'),
};
