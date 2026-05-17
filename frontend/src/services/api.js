import axios from 'axios';

import { API_BASE_URL } from '../constants/appConstants';

const healthCheckUrl = () => {
  const trimmed = API_BASE_URL.replace(/\/$/, '');
  const withoutApi = trimmed.replace(/\/api\/v1$/i, '');
  return `${withoutApi}/health`;
};

const api = axios.create({
  baseURL: API_BASE_URL,
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

api.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(error)
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
  check: () => axios.get(healthCheckUrl()),
};

export default api;

// Made with Bob
