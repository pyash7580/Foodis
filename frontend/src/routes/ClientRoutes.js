import React, { Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import ClientLayout from '../layouts/ClientLayout';

const Home = React.lazy(() => import('../pages/client/Home'));
const Search = React.lazy(() => import('../pages/client/Search'));
const RestaurantDetails = React.lazy(() => import('../pages/client/RestaurantDetails'));
const Cart = React.lazy(() => import('../pages/client/Cart'));
const Checkout = React.lazy(() => import('../pages/client/Checkout'));
const OrderTracking = React.lazy(() => import('../pages/client/OrderTracking'));
const ProfileLayout = React.lazy(() => import('../pages/client/profile/ProfileLayout'));
const ProfileHome = React.lazy(() => import('../pages/client/profile/ProfileHome'));
const Orders = React.lazy(() => import('../pages/client/profile/Orders'));
const AddressManagement = React.lazy(() => import('../pages/client/profile/AddressManagement'));
const WalletDetails = React.lazy(() => import('../pages/client/profile/WalletDetails'));
const Favorites = React.lazy(() => import('../pages/client/profile/Favorites'));
const Help = React.lazy(() => import('../pages/client/profile/Help'));
const SavedPayments = React.lazy(() => import('../pages/client/profile/SavedPayments'));

const PageLoader = () => (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-red-600"></div>
    </div>
);

const ClientRoutes = () => {
    return (
        <Suspense fallback={<PageLoader />}>
            <Routes>
                {/* All Client Routes Wrapped in Premium Layout */}
                <Route element={<ClientLayout />}>
                    <Route path="/" element={<Home />} />
                    <Route path="/search" element={<Search />} />
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
                </Route>
            </Routes>
        </Suspense>
    );
};

export default ClientRoutes;
