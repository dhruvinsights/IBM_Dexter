import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('dexter-token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('dexter-token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Reviews API
export const reviewsAPI = {
  getAll: () => api.get('/reviews'),
  getById: (id) => api.get(`/reviews/${id}`),
};

// Repositories API
export const repositoriesAPI = {
  getAll: () => api.get('/repositories'),
  getById: (id) => api.get(`/repositories/${id}`),
  create: (data) => api.post('/repositories', data),
  update: (id, data) => api.put(`/repositories/${id}`, data),
  delete: (id) => api.delete(`/repositories/${id}`),
};

// Pull Requests API
export const pullRequestsAPI = {
  getAll: () => api.get('/pull-requests'),
  getById: (id) => api.get(`/pull-requests/${id}`),
  review: (id) => api.post(`/pull-requests/${id}/review`),
};

// Health check
export const healthAPI = {
  check: () => axios.get('http://localhost:8000/health'),
};

export default api;

// Made with Bob
