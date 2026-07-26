import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.DEV ? 'http://localhost:8000/api' : '/api',
});

// Request interceptor to attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle 401s (Unauthenticated)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // If we had a refresh token endpoint, we would handle it here.
    // For now, if we get 401, we just clear auth and redirect to login if not already there.
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
