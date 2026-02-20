import React, { useState, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const RiderProtectedRoute = ({ children }) => {
    useAuth(); // Subscribe to context updates
    // const { isAuthenticated, logout } = useAuth(); // Unused
    const location = useLocation();
    const [isVerified, setIsVerified] = useState(null);
    const [status, setStatus] = useState(null);

    useEffect(() => {
        const verifyRider = async () => {
            const token = localStorage.getItem('token_rider');

            if (!token) {
                setIsVerified(false);
                return;
            }

            try {
                const res = await axios.get(`${API_BASE_URL}/api/rider/login-status/`, {
                    headers: { Authorization: `Bearer ${token}`, 'X-Role': 'RIDER' }
                });

                if (res.data) {
                    setIsVerified(true);
                    setStatus(res.data); // Store the entire response object
                }
            } catch (err) {
                console.error("Rider verification failed", err);
                if (err.response && err.response.status === 401) {
                    setIsVerified(false);
                } else {
                    const errorMsg = err.response?.data?.error || err.message;
                    alert(`Network Error: Verification failed (${errorMsg}). Please refresh.`);
                    setIsVerified(null);
                }
            }
        };

        verifyRider();
    }, [location.pathname]);

    if (isVerified === null) {
        return <div className="flex h-screen items-center justify-center">Verifying Access...</div>;
    }

    if (!isVerified) {
        return <Navigate to="/rider/login" state={{ from: location }} replace />;
    }

    const { redirect, step } = status;
    const path = location.pathname;

    // Strict Redirection Logic based on single source of truth
    if (redirect === 'blocked' && !path.includes('status')) {
        return <Navigate to="/rider/status" replace />;
    }

    if (redirect === 'dashboard' && (path.includes('onboarding') || path.includes('status'))) {
        return <Navigate to="/rider/dashboard" replace />;
    }

    if (redirect === 'status' && !path.includes('status')) {
        return <Navigate to="/rider/status" replace />;
    }

    if (redirect === 'rejected' && !path.includes('status')) {
        return <Navigate to="/rider/status" replace />;
    }

    if (redirect === 'onboarding' && !path.includes('onboarding') && !path.includes('status')) {
        return <Navigate to="/rider/onboarding" state={{ step }} replace />;
    }



    return children;
};

export default RiderProtectedRoute;
