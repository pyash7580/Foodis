const LOCAL_HOSTS = new Set(['localhost', '127.0.0.1']);

const normalizeUrl = (url) => (url || '').replace(/\/+$/, '');

const isLocalAddress = (url) => {
    if (!url) return false;
    try {
        const parsed = new URL(url);
        return LOCAL_HOSTS.has(parsed.hostname);
    } catch {
        return /(localhost|127\.0\.0\.1)/i.test(url);
    }
};

const toWsUrlFromHttp = (httpUrl) => {
    try {
        const parsed = new URL(httpUrl);
        const protocol = parsed.protocol === 'https:' ? 'wss:' : 'ws:';
        return `${protocol}//${parsed.host}/ws`;
    } catch {
        return '';
    }
};

const getBaseUrl = () => {
    const isLocalFrontend = LOCAL_HOSTS.has(window.location.hostname);
    const envApiUrl = normalizeUrl(process.env.REACT_APP_API_URL || '');

    if (isLocalFrontend) {
        // On localhost, prefer CRA proxy for local APIs to avoid CORS issues.
        // If env points to a remote backend, respect it.
        if (envApiUrl && !isLocalAddress(envApiUrl)) {
            return envApiUrl;
        }
        return '';
    }

    // Respect explicit env first. If env incorrectly points to localhost in production,
    // ignore it and fall back to empty string (will use default/proxy)
    if (envApiUrl) {
        if (isLocalAddress(envApiUrl)) {
            return '';
        }
        return envApiUrl;
    }

    return '';
};

const getWsUrl = () => {
    const isLocalFrontend = LOCAL_HOSTS.has(window.location.hostname);
    const envWsUrl = normalizeUrl(process.env.REACT_APP_WS_URL || '');
    const envApiUrl = normalizeUrl(process.env.REACT_APP_API_URL || '');

    if (isLocalFrontend) {
        // Keep local WS unless explicit remote WS is provided.
        if (envWsUrl && !isLocalAddress(envWsUrl)) {
            return envWsUrl;
        }
        if (envApiUrl && !isLocalAddress(envApiUrl)) {
            const derivedRemote = toWsUrlFromHttp(envApiUrl);
            if (derivedRemote) return derivedRemote;
        }
        return process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
    }

    if (envWsUrl) {
        if (isLocalAddress(envWsUrl)) {
            return '';
        }
        return envWsUrl;
    }

    if (envApiUrl) {
        const derived = toWsUrlFromHttp(envApiUrl);
        if (derived && (isLocalFrontend || !isLocalAddress(derived))) {
            return derived;
        }
    }

    return '';
};

export const API_BASE_URL = getBaseUrl();
export const WS_BASE_URL = getWsUrl();

export const API_URLS = {
    RESTAURANTS: `${API_BASE_URL}/api/client/restaurants/`,
    AUTH: `${API_BASE_URL}/api/auth/`,
    CLIENT: `${API_BASE_URL}/api/client/`,
};
