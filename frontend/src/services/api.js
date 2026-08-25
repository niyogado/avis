const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

function getToken() {
  try {
    return localStorage.getItem('avis_token');
  } catch {
    return null;
  }
}

function headers(isJson = true) {
  const token = getToken();
  const h = {};
  if (isJson) h['Content-Type'] = 'application/json';
  if (token) h['Authorization'] = `Bearer ${token}`;
  return h;
}

async function handleResponse(res) {
  const contentType = res.headers.get('content-type') || '';
  const isJson = contentType.includes('application/json');
  const data = isJson ? await res.json() : null;
  if (!res.ok) {
    const error = new Error(data?.detail || res.statusText || 'API Error');
    error.status = res.status;
    error.data = data;
    throw error;
  }
  return data;
}

export default {
  get: async (path) => {
    const res = await fetch(`${API_BASE}${path}`, { headers: headers() });
    return handleResponse(res);
  },
  post: async (path, body, isJson = true) => {
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: headers(isJson),
      body: isJson ? JSON.stringify(body) : body,
    });
    return handleResponse(res);
  },
  put: async (path, body) => {
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'PUT',
      headers: headers(),
      body: JSON.stringify(body),
    });
    return handleResponse(res);
  },
  del: async (path) => {
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'DELETE',
      headers: headers(),
    });
    return handleResponse(res);
  },
};
