
import React, { createContext, useState, useEffect, useContext, useCallback, useMemo } from 'react';
import axios from 'axios';
import { useLocation } from 'react-router-dom';
import { API_BASE_URL } from '../config';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

const getStorageKey = (pathname) => {
    const path = pathname || window.location.pathname;
    if (path.startsWith('/restaurant')) return 'token_restaurant';
    if (path.startsWith('/rider')) return 'token_rider';
    if (path.startsWith('/admin')) return 'token_admin';
    return 'token_client';
};

export const AuthProvider = ({ children }) => {
    const location = useLocation();
    const [user, setUser] = useState(null);
    // Initialize using current path
    const [token, setToken] = useState(localStorage.getItem(getStorageKey(location.pathname)));
    const [loading, setLoading] = useState(true);

    // Switch token when Realm changes (e.g. /client -> /restaurant)
    useEffect(() => {
        const expectedKey = getStorageKey(location.pathname);
        const storedToken = localStorage.getItem(expectedKey);

        // Only update if the token in state doesn't match what's expected for this route
        // This handles the case where user navigates from Client -> Restaurant
        if (token !== storedToken) {
            console.log(`Switching Auth Realm: ${expectedKey}`);
            setToken(storedToken);
            if (storedToken) {
                const role = expectedKey.replace('token_', '').toUpperCase();
                axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
                axios.defaults.headers.common['X-Role'] = role;
            } else {
                delete axios.defaults.headers.common['Authorization'];
                delete axios.defaults.headers.common['X-Role'];
                setUser(null); // Clear user if no token for this realm
            }
        }
    }, [location.pathname, token]);

    // GLOBAL AXIOS INTERCEPTOR for 401s
    useEffect(() => {
        const interceptor = axios.interceptors.response.use(
            response => response,
            error => {
                if (error.response && error.response.status === 401) {
                    console.warn("Unauthorized (401) detected. Clearing session.");
                    const key = getStorageKey(location.pathname);
                    localStorage.removeItem(key);
                    setToken(null); // This triggers the logic to remove axios headers
                    setUser(null);
                }
                return Promise.reject(error);
            }
        );

        return () => {
            axios.interceptors.response.eject(interceptor);
        };
    }, [location.pathname]);

    // Configure Axios defaults (keep existing check)
    // We strictly sync axios headers with state `token`
    useEffect(() => {
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            const key = getStorageKey(location.pathname);
            const role = key.replace('token_', '').toUpperCase();
            axios.defaults.headers.common['X-Role'] = role;
        } else {
            delete axios.defaults.headers.common['Authorization'];
            delete axios.defaults.headers.common['X-Role'];
        }
    }, [token, location.pathname]);


    useEffect(() => {
        const loadUser = async () => {
            if (token) {
                try {
                    const response = await axios.get(`${API_BASE_URL}/api/auth/profile/`);
                    setUser(response.data);
                } catch (error) {
                    console.error("Failed to load user", error);
                    // 401 handled by interceptor now, but good to keep safe fallback
                }
            } else {
                setUser(null);
            }
            setLoading(false);
        };
        loadUser();
    }, [token]);

    const login = useCallback(async (email, password, expectedRole = null) => {
        try {
            const res = await axios.post(`${API_BASE_URL}/api/auth/login/`, { email, password });
            const { token, user } = res.data;

            if (expectedRole && user?.role !== expectedRole) {
                return {
                    success: false,
                    error: `This account is registered as ${user?.role || 'UNKNOWN'}. Please use the correct login page.`,
                    code: 'ROLE_MISMATCH',
                    registered_role: user?.role || null,
                };
            }

            const key = getStorageKey(location.pathname);
            localStorage.setItem(key, token);
            setToken(token);
            setUser(user);
            const role = key.replace('token_', '').toUpperCase();
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            axios.defaults.headers.common['X-Role'] = role;
            return { success: true };
        } catch (error) {
            console.error("Login error", error);
            return {
                success: false,
                error: error.response?.data?.message || error.response?.data?.error || "Login failed",
                code: error.response?.data?.error || null,
            };
        }
    }, [location.pathname]);

    const sendOtp = useCallback(async (contact, type = 'phone') => {
        try {
            const payload = (type === 'phone' || type === 'mobile') ? { phone: contact } : { email: contact };
            const res = await axios.post(`${API_BASE_URL}/api/auth/send-otp/`, payload);
            return { success: true, otp: res.data.otp, message: res.data.message };
        } catch (error) {
            console.error("OTP Error:", error);
            let updateMsg = "Failed to send OTP";
            if (error.response) {
                if (error.response.data && typeof error.response.data === 'object') {
                    const messages = Object.values(error.response.data).flat();
                    if (messages.length > 0) updateMsg = messages.join(', ');
                }
                else if (error.response.statusText) {
                    updateMsg = `${error.response.status}: ${error.response.statusText}`;
                }
            }
            return {
                success: false,
                error: error.response?.data?.message || updateMsg,
                code: error.response?.data?.error || null,
            };
        }
    }, []);

    const verifyOtp = useCallback(async (contact, otp, type = 'phone', name = '', role = 'CLIENT') => {
        try {
            const payload = (type === 'phone' || type === 'mobile')
                ? { phone: contact, otp_code: otp, name, role }
                : { email: contact, otp_code: otp, name, role };

            const res = await axios.post(`${API_BASE_URL}/api/auth/verify-otp/`, payload);

            if (res.data.action === 'LOGIN' && res.data.token) {
                const { token, user } = res.data;
                const key = getStorageKey(location.pathname);

                localStorage.setItem(key, token);
                const roleHeader = key.replace('token_', '').toUpperCase();
                axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
                axios.defaults.headers.common['X-Role'] = roleHeader;
                setToken(token);
                setUser(user);
            }

            return { success: true, ...res.data };
        } catch (error) {
            console.error("OTP Verification Error:", error);
            return {
                success: false,
                error: error.response?.data?.error || "Invalid OTP",
                message: error.response?.data?.message || "Invalid OTP",
                code: error.response?.data?.error || null,
            };
        }
    }, [location.pathname]);

    const register = useCallback(async (regData) => {
        try {
            const res = await axios.post(`${API_BASE_URL}/api/auth/register/`, regData);
            const { token, user } = res.data;

            const key = getStorageKey(location.pathname);

            localStorage.setItem(key, token);
            const roleHeader = key.replace('token_', '').toUpperCase();
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            axios.defaults.headers.common['X-Role'] = roleHeader;
            setToken(token);
            setUser(user);
            return { success: true, ...res.data };
        } catch (error) {
            console.error("Registration Error:", error);
            return {
                success: false,
                error: error.response?.data?.error || "Registration failed"
            };
        }
    }, [location.pathname]);

    const logout = useCallback(async () => {
        const realm = location.pathname.startsWith('/restaurant') ? 'restaurant' :
            location.pathname.startsWith('/rider') ? 'rider' :
                location.pathname.startsWith('/admin') ? 'admin' : 'client';

        try {
            if (token) {
                await axios.post(`${API_BASE_URL}/api/auth/logout/`);
            }
        } catch (e) {
            console.warn("Backend logout failed or session already expired", e);
        }

        const key = getStorageKey(location.pathname);
        localStorage.removeItem(key);

        setToken(null);
        setUser(null);
        delete axios.defaults.headers.common['Authorization'];
        delete axios.defaults.headers.common['X-Role'];

        window.location.href = realm === 'client' ? '/login' : `/${realm}/login`;
    }, [location.pathname, token]);

    const value = useMemo(() => ({
        user,
        setUser,
        token,
        loading,
        login,
        logout,
        sendOtp,
        verifyOtp,
        register,
        isAuthenticated: !!user
    }), [user, token, loading, login, logout, sendOtp, verifyOtp, register]);

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export default AuthContext;
