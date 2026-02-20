export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8001';
export const API_URLS = {
    RESTAURANTS: `${API_BASE_URL}/api/client/restaurants/`,
    AUTH: `${API_BASE_URL}/api/auth/`,
    CLIENT: `${API_BASE_URL}/api/client/`,
};

export const WS_BASE_URL = process.env.REACT_APP_WS_URL || 'ws://127.0.0.1:8001/ws';
