
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import AdminLayout from '../layouts/AdminLayout';
import AdminProtectedRoute from './AdminProtectedRoute';

import AdminDashboard from '../pages/admin/AdminDashboard';
import UserManagement from '../pages/admin/UserManagement';
import ReviewManagement from '../pages/admin/ReviewManagement';
import SystemSettings from '../pages/admin/SystemSettings';
// Import other pages as they are created
import RestaurantManagement from '../pages/admin/RestaurantManagement';

import RiderManagement from '../pages/admin/RiderManagement';
import OrderManagement from '../pages/admin/OrderManagement';
import FinanceManagement from '../pages/admin/FinanceManagement';

const AdminRoutes = () => {
    return (
        <AdminProtectedRoute>
            <AdminLayout>
                <Routes>
                    <Route path="/dashboard" element={<AdminDashboard />} />

                    {/* Management Routes */}
                    <Route path="/users" element={<UserManagement />} />
                    <Route path="/restaurants" element={<RestaurantManagement />} />
                    <Route path="/riders" element={<RiderManagement />} />
                    <Route path="/orders" element={<OrderManagement />} />
                    <Route path="/finance" element={<FinanceManagement />} />

                    <Route path="/reviews" element={<ReviewManagement />} />
                    <Route path="/settings" element={<SystemSettings />} />

                    <Route path="/" element={<Navigate to="/admin/dashboard" replace />} />
                </Routes>
            </AdminLayout>
        </AdminProtectedRoute>
    );
};

export default AdminRoutes;
