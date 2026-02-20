
import React, { useState, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const AdminProtectedRoute = ({ children }) => {
    useAuth(); // Keep hook to subscribe to auth changes, but we check token manually below
    // const { isAuthenticated, logout } = useAuth(); // Unused
    const location = useLocation();
    const [isAuthorized, setIsAuthorized] = useState(null);

    useEffect(() => {
        const verifyAdmin = async () => {
            const token = localStorage.getItem('token_admin');

            if (!token) {
                setIsAuthorized(false);
                return;
            }

            try {
                // Verify if the user is actually an ADMIN
                const res = await axios.get(`${API_BASE_URL}/api/auth/profile/`, {
                    headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' }
                });

                if (res.data && res.data.role === 'ADMIN') {
                    setIsAuthorized(true);
                } else {
                    console.error("User is not an admin");
                    setIsAuthorized(false);
                }
            } catch (err) {
                console.error("Admin verification failed", err);
                setIsAuthorized(false);
            }
        };

        verifyAdmin();
    }, [location.pathname]);

    if (isAuthorized === null) {
        return <div className="flex h-screen items-center justify-center font-bold text-gray-500">Verifying Admin Access...</div>;
    }

    if (!isAuthorized) {
        return <Navigate to="/admin/login" state={{ from: location }} replace />;
    }

    return children;
};

export default AdminProtectedRoute;
