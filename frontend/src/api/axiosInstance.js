import axios from 'axios';

// Get API URL from environment variables
// Fallback only if running on localhost (for development)
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_URL = process.env.REACT_APP_API_URL || (isLocalhost ? 'http://localhost:8000' : '');

const axiosInstance = axios.create({
    baseURL: API_URL,
    timeout: 30000,
    headers: { 'Content-Type': 'application/json' },
});

axiosInstance.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

// Add retry logic for Render cold starts (8000ms delay)
const delay = ms => new Promise(res => setTimeout(res, ms));

axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
        const config = error.config;

        // Handle 401 token expiration
        if (error.response?.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            return Promise.reject(error);
        }

        // Retry logic for 502/Network errors (Render cold start)
        if (!config || !config.retry) {
            config.retry = 0;
        }

        if (config.retry < 3 && (!error.response || error.response.status >= 500)) {
            config.retry += 1;
            console.log(`Retrying request (${config.retry}/3) due to Render cold start...`);
            await delay(8000); // 8-second delay
            return axiosInstance(config);
        }

        return Promise.reject(error);
    }
);

export default axiosInstance;
