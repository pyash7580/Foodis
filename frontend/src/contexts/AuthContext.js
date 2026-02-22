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

// ✅ FIX 1: Normalize phone to always send +91 prefix consistently
//    so send-otp and verify-otp use the same format as the OTP cache key
const normalizePhone = (phone) => {
    if (!phone) return '';
    const digits = phone.replace(/\D/g, '');
    const last10 = digits.slice(-10);
    return `+91${last10}`;
};

export const AuthProvider = ({ children }) => {
    const location = useLocation();
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem(getStorageKey(location.pathname)));
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const expectedKey = getStorageKey(location.pathname);
        const storedToken = localStorage.getItem(expectedKey);
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
                setUser(null);
            }
        }
    }, [location.pathname, token]);

    useEffect(() => {
        const interceptor = axios.interceptors.response.use(
            response => response,
            error => {
                if (error.response && error.response.status === 401) {
                    console.warn("Unauthorized (401) detected. Clearing session.");
                    const key = getStorageKey(location.pathname);
                    localStorage.removeItem(key);
                    setToken(null);
                    setUser(null);
                }
                return Promise.reject(error);
            }
        );
        return () => {
            axios.interceptors.response.eject(interceptor);
        };
    }, [location.pathname]);

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
            // ✅ FIX 2: Always send phone with +91 prefix so OTP is cached under consistent key
            const phone = (type === 'phone' || type === 'mobile') ? normalizePhone(contact) : null;
            const payload = phone ? { phone } : { email: contact };

            console.log('[sendOtp] Sending payload:', payload); // debug aid

            const res = await axios.post(`${API_BASE_URL}/api/auth/send-otp/`, payload);
            return { success: true, otp: res.data.otp, message: res.data.message };
        } catch (error) {
            console.error("OTP Error:", error);
            let updateMsg = "Failed to send OTP";
            if (error.response) {
                if (error.response.data && typeof error.response.data === 'object') {
                    const messages = Object.values(error.response.data).flat();
                    if (messages.length > 0) updateMsg = messages.join(', ');
                } else if (error.response.statusText) {
                    updateMsg = `${error.response.status}: ${error.response.statusText}`;
                }
            }
            return {
                success: false,
                // ✅ FIX 3: Prefer human-readable .message over raw error code
                error: error.response?.data?.message || updateMsg,
                code: error.response?.data?.error || null,
            };
        }
    }, []);

    const verifyOtp = useCallback(async (contact, otp, type = 'phone', name = '', role = 'CLIENT') => {
        try {
            // ✅ FIX 4: Same normalizePhone so verify-otp key matches send-otp key in cache
            const phone = (type === 'phone' || type === 'mobile') ? normalizePhone(contact) : null;

            const payload = phone
                ? { phone, otp_code: String(otp), role }  // ✅ FIX 5: otp as String, skip empty name
                : { email: contact, otp_code: String(otp), role };

            // Only include name if it's actually provided (avoids serializer rejecting empty string)
            if (name && name.trim()) payload.name = name.trim();

            console.log('[verifyOtp] Sending payload:', payload); // debug aid

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
            // ✅ FIX 6: Show .message (human readable) not .error (code like "SERVER_ERROR")
            //    Fallback chain: message → error code → generic
            const errData = error.response?.data;
            return {
                success: false,
                error: errData?.message || errData?.error || "Invalid or expired OTP. Please try again.",
                message: errData?.message || errData?.error || "Invalid or expired OTP. Please try again.",
                code: errData?.error || null,
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