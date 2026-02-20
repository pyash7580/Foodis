
import React, { useEffect, useState } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { API_BASE_URL } from '../config';

const RestaurantProtectedRoute = () => {
    const { user, token, loading } = useAuth();
    const [statusLoading, setStatusLoading] = useState(true);
    const [restaurantStatus, setRestaurantStatus] = useState(null); // 'NONE', 'PENDING', 'APPROVED', 'REJECTED'
    const location = useLocation();
    // const navigate = useNavigate(); // Unused

    useEffect(() => {
        const checkStatus = async () => {
            if (user && user.role === 'RESTAURANT' && token) {
                try {
                    // Fetch restaurant details for this user
                    const res = await axios.get(`${API_BASE_URL}/api/restaurant/restaurant/`, {
                        headers: { Authorization: `Bearer ${token}`, 'X-Role': 'RESTAURANT' }
                    });

                    // Check if array (ViewSet list) or object
                    const restaurants = Array.isArray(res.data) ? res.data : [res.data];

                    if (restaurants.length === 0) {
                        setRestaurantStatus('NONE');
                    } else {
                        setRestaurantStatus(restaurants[0].status);
                    }
                } catch (error) {
                    console.error("Failed to check restaurant status", error);
                    setRestaurantStatus('NONE');
                }
            }
            setStatusLoading(false);
        };

        if (!loading) {
            checkStatus();
        }
    }, [user, loading, token]);

    if (loading || statusLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-white">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-red-600"></div>
            </div>
        );
    }

    // 1. Check Authentication & Role
    if (!user || user.role !== 'RESTAURANT') {
        return <Navigate to="/restaurant/login" replace />;
    }

    // 2. Handle Status Redirection Logic
    const currentPath = location.pathname;

    // A. No Restaurant Created -> Must go to Onboarding
    if (restaurantStatus === 'NONE') {
        if (currentPath !== '/restaurant/onboarding') {
            return <Navigate to="/restaurant/onboarding" replace />;
        }
    }

    // B. Pending Approval
    else if (restaurantStatus === 'PENDING') {
        if (currentPath !== '/restaurant/pending') {
            return <Navigate to="/restaurant/pending" replace />;
        }
    }

    // C. Rejected
    else if (restaurantStatus === 'REJECTED') {
        if (currentPath !== '/restaurant/rejected') {
            return <Navigate to="/restaurant/rejected" replace />;
        }
    }

    // D. Approved -> Allow access to Dashboard, but NOT onboarding/status pages
    else if (restaurantStatus === 'APPROVED') {
        if (['/restaurant/onboarding', '/restaurant/pending', '/restaurant/rejected'].includes(currentPath)) {
            return <Navigate to="/restaurant/dashboard" replace />;
        }
    }

    return <Outlet />;
};

export default RestaurantProtectedRoute;
