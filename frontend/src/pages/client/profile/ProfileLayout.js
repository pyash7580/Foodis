
import React from 'react';
import { Link, useLocation, Outlet, useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../../../contexts/AuthContext';

const ProfileLayout = () => {
    const { user, logout } = useAuth();
    const location = useLocation();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const isActive = (path) => {
        return location.pathname === path ? 'bg-red-50 text-red-600 font-bold border-l-4 border-red-600' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900';
    };

    if (!user) return <Navigate to="/login" replace />;

    return (
        <div className="bg-gray-50 min-h-screen relative">
            {/* Mobile App Bar */}
            <div className="md:hidden bg-white flex items-center px-4 h-14 border-b border-gray-100 sticky top-0 z-40 shadow-sm">
                <button
                    onClick={() => navigate('/client')}
                    className="p-2 -ml-2 text-gray-800 focus:outline-none"
                >
                    <span className="text-xl leading-none">←</span>
                </button>
                <h1 className="ml-2 text-lg font-black text-gray-900 truncate">My Account</h1>
            </div>

            <div className="w-full mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
                <div className="flex flex-col lg:flex-row gap-8">
                    {/* Sidebar */}
                    <aside className="w-full lg:w-1/4">
                        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden lg:sticky lg:top-8">
                            <div className="p-6 border-b border-gray-50">
                                <div className="flex items-center space-x-4">
                                    <div className="h-16 w-16 rounded-full bg-red-100 flex items-center justify-center text-red-600 text-2xl font-bold border border-red-200">
                                        {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <h2 className="text-lg font-bold text-gray-900 truncate">{user.name}</h2>
                                        <p className="text-sm text-gray-500 truncate">{user.phone}</p>
                                    </div>
                                </div>
                            </div>
                            <nav className="p-2 space-y-1">
                                <Link to="/client/profile" className={`flex items-center px-4 py-3 text-sm transition-all duration-200 rounded-r-lg ${isActive('/client/profile')}`}>
                                    <span className="w-8 text-lg">👤</span> Profile
                                </Link>
                                <Link to="/client/orders" className={`flex items-center px-4 py-3 text-sm transition-all duration-200 rounded-r-lg ${isActive('/client/orders')}`}>
                                    <span className="w-8 text-lg">📦</span> Orders
                                </Link>
                                <Link to="/client/addresses" className={`flex items-center px-4 py-3 text-sm transition-all duration-200 rounded-r-lg ${isActive('/client/addresses')}`}>
                                    <span className="w-8 text-lg">📍</span> Addresses
                                </Link>
                                <Link to="/client/favourites" className={`flex items-center px-4 py-3 text-sm transition-all duration-200 rounded-r-lg ${isActive('/client/favourites')}`}>
                                    <span className="w-8 text-lg">❤️</span> Favourites
                                </Link>
                                <Link to="/client/wallet" className={`flex items-center px-4 py-3 text-sm transition-all duration-200 rounded-r-lg ${isActive('/client/wallet')}`}>
                                    <span className="w-8 text-lg">👛</span> Money & Wallets
                                </Link>
                                <Link to="/client/payments" className={`flex items-center px-4 py-3 text-sm transition-all duration-200 rounded-r-lg ${isActive('/client/payments')}`}>
                                    <span className="w-8 text-lg">💳</span> Saved Payments
                                </Link>
                                <Link to="/client/help" className={`flex items-center px-4 py-3 text-sm transition-all duration-200 rounded-r-lg ${isActive('/client/help')}`}>
                                    <span className="w-8 text-lg">❓</span> Help & Support
                                </Link>
                                <button onClick={handleLogout} className="w-full flex items-center px-4 py-3 text-sm text-gray-600 hover:bg-red-50 hover:text-red-600 transition-all duration-200 rounded-r-lg text-left">
                                    <span className="w-8 text-lg">🚪</span> Logout
                                </button>
                            </nav>
                        </div>
                    </aside>

                    {/* Main Content */}
                    <main className="w-full lg:w-3/4">
                        <Outlet />
                    </main>
                </div>
            </div>
        </div>
    );
};

export default ProfileLayout;
