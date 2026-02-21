const getBaseUrl = () => {
    if (process.env.REACT_APP_API_URL) return process.env.REACT_APP_API_URL;
    // If on localhost, use local backend. Otherwise, use the Render backend.
    return window.location.origin.includes('localhost')
        ? 'http://localhost:8000'
        : 'https://foodis-jpvq.onrender.com';
};

const getWsUrl = () => {
    if (process.env.REACT_APP_WS_URL) return process.env.REACT_APP_WS_URL;
    // If on localhost, use local WS. Otherwise, use the Render WS.
    return window.location.origin.includes('localhost')
        ? 'ws://localhost:8000/ws'
        : 'wss://foodis-jpvq.onrender.com/ws';
};

export const API_BASE_URL = getBaseUrl();
export const WS_BASE_URL = getWsUrl();

export const API_URLS = {
    RESTAURANTS: `${API_BASE_URL}/api/client/restaurants/`,
    AUTH: `${API_BASE_URL}/api/auth/`,
    CLIENT: `${API_BASE_URL}/api/client/`,
};
