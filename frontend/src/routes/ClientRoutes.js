
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Home from '../pages/client/Home';
import RestaurantDetails from '../pages/client/RestaurantDetails';
import Cart from '../pages/client/Cart';
import Checkout from '../pages/client/Checkout';
import OrderTracking from '../pages/client/OrderTracking';
import ProfileLayout from '../pages/client/profile/ProfileLayout';
import ProfileHome from '../pages/client/profile/ProfileHome';
import Orders from '../pages/client/profile/Orders';
import AddressManagement from '../pages/client/profile/AddressManagement';
import WalletDetails from '../pages/client/profile/WalletDetails';
import Favorites from '../pages/client/profile/Favorites';
import Help from '../pages/client/profile/Help';
import SavedPayments from '../pages/client/profile/SavedPayments';

const ClientRoutes = () => {
    return (
        <React.Suspense fallback={<div className="min-h-screen bg-gray-50 flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-red-600"></div></div>}>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/search" element={<div className="p-8 text-center text-gray-500">Search Feature Coming Soon</div>} />
                <Route path="/cart" element={<Cart />} />
                <Route path="/checkout" element={<Checkout />} />
                <Route path="/track/:orderId" element={<OrderTracking />} />
                <Route path="/restaurants/:id" element={<RestaurantDetails />} />

                {/* Profile Section wrapped in Layout */}
                <Route element={<ProfileLayout />}>
                    <Route path="/profile" element={<ProfileHome />} />
                    <Route path="/orders" element={<Orders />} />
                    <Route path="/addresses" element={<AddressManagement />} />
                    <Route path="/wallet" element={<WalletDetails />} />
                    <Route path="/favourites" element={<Favorites />} />
                    <Route path="/help" element={<Help />} />
                    <Route path="/payments" element={<SavedPayments />} />
                </Route>

                <Route path="*" element={<div className="p-8 text-center text-red-500">Page Not Found</div>} />
            </Routes>
        </React.Suspense>
    );
};

export default ClientRoutes;
