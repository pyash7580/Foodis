import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || '';
// Empty string = use proxy (localhost dev)
// Full URL = production (Vercel)

const axiosInstance = axios.create({
    baseURL: API_URL,
    timeout: 30000,
    headers: { 'Content-Type': 'application/json' },
});

// Add JWT token to every request
axiosInstance.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Handle 401 — token expired
axiosInstance.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
        }
        return Promise.reject(error);
    }
);

export default axiosInstance;
