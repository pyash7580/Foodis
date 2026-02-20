
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Dashboard from '../pages/restaurant/Dashboard';
import MenuManagement from '../pages/restaurant/MenuManagement';
import EarningsReport from '../pages/restaurant/EarningsReport';
import RestaurantProtectedRoute from './RestaurantProtectedRoute';
import RestaurantOnboarding from '../pages/restaurant/onboarding/RestaurantOnboarding';
import PendingApproval from '../pages/restaurant/onboarding/PendingApproval';
import Rejected from '../pages/restaurant/onboarding/Rejected';
import RestaurantProfile from '../pages/restaurant/RestaurantProfile';

const RestaurantRoutes = () => {
    return (
        <Routes>
            <Route element={<RestaurantProtectedRoute />}>
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/menu" element={<MenuManagement />} />
                <Route path="/earnings" element={<EarningsReport />} />
                <Route path="/profile" element={<RestaurantProfile />} />

                {/* Onboarding Routes (Protected by Logic) */}
                <Route path="/onboarding" element={<RestaurantOnboarding />} />
                <Route path="/pending" element={<PendingApproval />} />
                <Route path="/rejected" element={<Rejected />} />
            </Route>
            <Route path="*" element={<div className="p-4"><h1>404 Not Found</h1></div>} />
        </Routes>
    );
};

export default RestaurantRoutes;
