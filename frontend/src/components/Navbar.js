
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useCart } from '../contexts/CartContext';

const Navbar = () => {
    const { user, logout } = useAuth();
    const { getCartCount } = useCart();
    const navigate = useNavigate();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isMoreOpen, setIsMoreOpen] = useState(false);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav className="bg-white shadow-md sticky top-0 z-50">
            <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex items-center">
                        <Link to="/client" className="flex-shrink-0 flex items-center">
                            <h1 className="text-3xl font-extrabold text-red-600 italic">Foodis</h1>
                        </Link>
                        <div className="hidden sm:ml-8 sm:flex sm:space-x-1">
                            {[
                                { name: 'Home', path: '/client' },
                                { name: 'My Orders', path: '/client/orders' },
                                { name: 'Favourites', path: '/client/favourites' },
                                { name: 'Help & Support', path: '/client/help' }
                            ].map((link) => (
                                <Link
                                    key={link.path}
                                    to={link.path}
                                    className="relative px-4 py-2 text-sm font-bold text-gray-500 hover:text-red-600 transition-all duration-300 group flex items-center h-16"
                                >
                                    <span className="relative z-10">{link.name}</span>
                                    {/* Premium Hover Underline */}
                                    <span className="absolute bottom-0 left-1/2 w-0 h-1 bg-red-600 transition-all duration-300 group-hover:w-full group-hover:left-0 rounded-t-full"></span>
                                    {/* Subtle Background Highlight */}
                                    <span className="absolute inset-x-1 inset-y-3 bg-red-50 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-0"></span>
                                </Link>
                            ))}
                        </div>
                    </div>
                    <div className="flex items-center space-x-4">


                        {/* Cart Icon with Badge */}
                        <Link
                            to="/client/cart"
                            className="relative text-gray-500 hover:text-red-600 transition-colors duration-200 group"
                        >
                            <div className="relative">
                                <span className="text-2xl">🛒</span>
                                {getCartCount() > 0 && (
                                    <span className="absolute -top-2 -right-2 bg-red-600 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center shadow-lg animate-pulse group-hover:animate-none">
                                        {getCartCount()}
                                    </span>
                                )}
                            </div>
                        </Link>

                        {user ? (
                            <div className="relative ml-3">
                                <div>
                                    <button
                                        onClick={() => { setIsMenuOpen(!isMenuOpen); setIsMoreOpen(false); }}
                                        className="flex text-sm border-2 border-transparent rounded-full focus:outline-none focus:border-gray-300 transition duration-150 ease-in-out"
                                    >
                                        <div className="h-8 w-8 rounded-full bg-red-100 flex items-center justify-center text-red-600 font-bold border border-red-200">
                                            {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
                                        </div>
                                    </button>
                                </div>
                                {isMenuOpen && (
                                    <div className="origin-top-right absolute right-0 mt-3 w-64 rounded-xl shadow-2xl py-1 bg-white ring-1 ring-black ring-opacity-5 z-50 overflow-hidden border border-gray-100">
                                        <div className="px-4 py-4 bg-gray-50 border-b flex items-center space-x-3">
                                            <div className="h-12 w-12 rounded-full bg-red-600 flex items-center justify-center text-white text-xl font-bold shadow-inner">
                                                {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <p className="text-base font-bold text-gray-900 truncate">{user.name}</p>
                                                <p className="text-xs text-gray-500 truncate flex items-center">
                                                    <span className="mr-1">📱</span> {user.phone || 'Set phone'}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="py-2">
                                            <Link
                                                to="/client/profile"
                                                onClick={() => setIsMenuOpen(false)}
                                                className="flex items-center px-4 py-2.5 text-sm text-gray-700 hover:bg-red-50 hover:text-red-600 transition-all duration-200"
                                            >
                                                <span className="mr-4 text-lg">👤</span> Profile
                                            </Link>
                                            <Link
                                                to="/client/orders"
                                                onClick={() => setIsMenuOpen(false)}
                                                className="flex items-center px-4 py-2.5 text-sm text-gray-700 hover:bg-red-50 hover:text-red-600 transition-all duration-200"
                                            >
                                                <span className="mr-4 text-lg">📦</span> Orders
                                            </Link>
                                            <Link
                                                to="/client/addresses"
                                                onClick={() => setIsMenuOpen(false)}
                                                className="flex items-center px-4 py-2.5 text-sm text-gray-700 hover:bg-red-50 hover:text-red-600 transition-all duration-200"
                                            >
                                                <span className="mr-4 text-lg">📍</span> Addresses
                                            </Link>
                                            <Link
                                                to="/client/favourites"
                                                onClick={() => setIsMenuOpen(false)}
                                                className="flex items-center px-4 py-2.5 text-sm text-gray-700 hover:bg-red-50 hover:text-red-600 transition-all duration-200"
                                            >
                                                <span className="mr-4 text-lg">❤️</span> Favourites
                                            </Link>
                                            <Link
                                                to="/client/wallet"
                                                onClick={() => setIsMenuOpen(false)}
                                                className="flex items-center px-4 py-2.5 text-sm text-gray-700 hover:bg-red-50 hover:text-red-600 transition-all duration-200"
                                            >
                                                <span className="mr-4 text-lg">👛</span> Wallet
                                            </Link>
                                        </div>
                                        <div className="border-t border-gray-100 pt-2 pb-1">
                                            <Link
                                                to="/client/help"
                                                onClick={() => setIsMenuOpen(false)}
                                                className="flex items-center px-4 py-2.5 text-sm text-gray-600 hover:bg-gray-50 transition-all duration-200 italic"
                                            >
                                                <span className="mr-4 text-lg">❓</span> Help & Support
                                            </Link>
                                            <button
                                                onClick={() => {
                                                    setIsMenuOpen(false);
                                                    handleLogout();
                                                }}
                                                className="flex items-center w-full text-left px-4 py-3 text-sm text-red-600 hover:bg-red-50 transition-all duration-200 font-bold border-t border-gray-100 mt-2"
                                            >
                                                <span className="mr-4 text-lg">🚪</span> Logout
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <Link to="/login" className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-full text-sm font-bold transition-colors duration-200 shadow-md">
                                Login
                            </Link>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
