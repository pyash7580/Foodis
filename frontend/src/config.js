const getBaseUrl = () => {
    if (process.env.REACT_APP_API_URL) return process.env.REACT_APP_API_URL;
    // Fallback to current origin if in production, or 8000 for standard dev
    return window.location.origin.includes('localhost') ? 'http://127.0.0.1:8000' : window.location.origin;
};

const getWsUrl = () => {
    if (process.env.REACT_APP_WS_URL) return process.env.REACT_APP_WS_URL;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.origin.includes('localhost') ? '127.0.0.1:8000' : window.location.host;
    return `${protocol}//${host}/ws`;
};

export const API_BASE_URL = getBaseUrl();
export const WS_BASE_URL = getWsUrl();

export const API_URLS = {
    RESTAURANTS: `${API_BASE_URL}/api/client/restaurants/`,
    AUTH: `${API_BASE_URL}/api/auth/`,
    CLIENT: `${API_BASE_URL}/api/client/`,
};
