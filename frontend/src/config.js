const getBaseUrl = () => {
    // If on localhost, ALWAYS use local backend to avoid .env caching issues
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    if (process.env.REACT_APP_API_URL) return process.env.REACT_APP_API_URL;
    return 'https://foodis-jpvq.onrender.com';
};

const getWsUrl = () => {
    // If on localhost, ALWAYS use local WS
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'ws://localhost:8000/ws';
    }
    if (process.env.REACT_APP_WS_URL) return process.env.REACT_APP_WS_URL;
    return 'wss://foodis-jpvq.onrender.com/ws';
};

export const API_BASE_URL = getBaseUrl();
export const WS_BASE_URL = getWsUrl();

export const API_URLS = {
    RESTAURANTS: `${API_BASE_URL}/api/client/restaurants/`,
    AUTH: `${API_BASE_URL}/api/auth/`,
    CLIENT: `${API_BASE_URL}/api/client/`,
};
