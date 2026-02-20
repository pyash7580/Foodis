import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import RiderLayout from '../components/rider/RiderLayout';
import RiderDashboardDesktop from '../pages/rider/RiderDashboardDesktop';
import RiderEarningsDesktop from '../pages/rider/RiderEarningsDesktop';
import RiderProfileDesktop from '../pages/rider/RiderProfileDesktop';
import RiderOnboarding from '../pages/rider/RiderOnboarding';
import RiderStatus from '../pages/rider/RiderStatus';
import ActiveOrder from '../pages/rider/ActiveOrder';
import RiderMissions from '../pages/rider/RiderMissions';
import NotificationCenter from '../pages/rider/NotificationCenter';
import RiderOrdersPage from '../pages/rider/RiderOrders';
import RiderProtectedRoute from './RiderProtectedRoute';

import { RiderProvider } from '../contexts/RiderContext';

const RiderRoutes = () => {
    return (
        <RiderProvider>
            <Routes>
                {/* Onboarding & Status (No Layout) */}
                <Route path="/onboarding" element={
                    <RiderProtectedRoute key="onboarding">
                        <RiderOnboarding />
                    </RiderProtectedRoute>
                } />
                <Route path="/status" element={
                    <RiderProtectedRoute key="status">
                        <RiderStatus />
                    </RiderProtectedRoute>
                } />

                {/* Desktop App Group */}
                <Route element={<RiderLayout />}>
                    <Route path="/dashboard" element={
                        <RiderProtectedRoute key="dashboard">
                            <RiderDashboardDesktop />
                        </RiderProtectedRoute>
                    } />
                    <Route path="/earnings" element={
                        <RiderProtectedRoute key="earnings">
                            <RiderEarningsDesktop />
                        </RiderProtectedRoute>
                    } />
                    <Route path="/profile" element={
                        <RiderProtectedRoute key="profile">
                            <RiderProfileDesktop />
                        </RiderProtectedRoute>
                    } />
                    <Route path="/order/:id" element={
                        <RiderProtectedRoute key="active-order">
                            <ActiveOrder />
                        </RiderProtectedRoute>
                    } />
                    <Route path="/missions" element={
                        <RiderProtectedRoute key="missions">
                            <RiderMissions />
                        </RiderProtectedRoute>
                    } />
                    <Route path="/notifications" element={
                        <RiderProtectedRoute key="notifications">
                            <NotificationCenter />
                        </RiderProtectedRoute>
                    } />
                    <Route path="/orders" element={
                        <RiderProtectedRoute key="orders">
                            <RiderOrdersPage />
                        </RiderProtectedRoute>
                    } />
                </Route>

                <Route path="/" element={<Navigate to="/rider/login" replace />} />
                <Route path="*" element={<div className="p-4"><h1>404 Not Found</h1></div>} />
            </Routes>
        </RiderProvider>
    );
};

export default RiderRoutes;
