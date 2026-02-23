import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://foodis-xtpw.onrender.com';

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

export default axiosInstance;
