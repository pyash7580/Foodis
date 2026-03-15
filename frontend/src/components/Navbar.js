
import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useCart } from '../contexts/CartContext';

const Navbar = () => {
    const { user, logout } = useAuth();
    const { getCartCount } = useCart();
    const navigate = useNavigate();
    const location = useLocation();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isDrawerOpen, setIsDrawerOpen] = useState(false);
    const dropdownRef = useRef(null);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (e) => {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
                setIsMenuOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // Close drawer on route change
    useEffect(() => {
        setIsDrawerOpen(false);
    }, [location.pathname]);

    // Prevent body scroll when drawer is open
    useEffect(() => {
        document.body.style.overflow = isDrawerOpen ? 'hidden' : '';
        return () => { document.body.style.overflow = ''; };
    }, [isDrawerOpen]);

    const navLinks = [
        { name: 'Home', path: '/client', icon: '🏠' },
        { name: 'My Orders', path: '/client/orders', icon: '📦' },
        { name: 'Favourites', path: '/client/favourites', icon: '❤️' },
        { name: 'Help & Support', path: '/client/help', icon: '❓' },
    ];

    return (
        <>
            <nav className="bg-white shadow-md sticky top-0 z-50">
                <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex items-center">
                            {/* Hamburger — mobile only */}
                            <button
                                className="mr-3 sm:hidden text-gray-600 hover:text-red-600 focus:outline-none w-11 h-11 flex items-center justify-center rounded-xl hover:bg-red-50 transition"
                                onClick={() => setIsDrawerOpen(true)}
                                aria-label="Open menu"
                            >
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                                </svg>
                            </button>

                            <Link to="/client" className="flex-shrink-0 flex items-center no-tap-fix">
                                <h1 className="text-2xl sm:text-3xl font-extrabold text-red-600 italic">Foodis</h1>
                            </Link>

                            {/* Desktop nav links */}
                            <div className="hidden sm:ml-8 sm:flex sm:space-x-1">
                                {navLinks.map((link) => (
                                    <Link
                                        key={link.path}
                                        to={link.path}
                                        className="relative px-4 py-2 text-sm font-bold text-gray-500 hover:text-red-600 transition-all duration-300 group flex items-center h-16 no-tap-fix"
                                    >
                                        <span className="relative z-10">{link.name}</span>
                                        <span className="absolute bottom-0 left-1/2 w-0 h-1 bg-red-600 transition-all duration-300 group-hover:w-full group-hover:left-0 rounded-t-full"></span>
                                        <span className="absolute inset-x-1 inset-y-3 bg-red-50 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-0"></span>
                                    </Link>
                                ))}
                            </div>
                        </div>

                        <div className="flex items-center space-x-2 sm:space-x-4">
                            {/* Cart Icon */}
                            <Link
                                to="/client/cart"
                                className="relative text-gray-500 hover:text-red-600 transition-colors duration-200 group w-11 h-11 flex items-center justify-center rounded-xl hover:bg-red-50 no-tap-fix"
                                style={{ minHeight: 'unset' }}
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
                                <div className="relative" ref={dropdownRef}>
                                    <button
                                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                                        className="flex text-sm border-2 border-transparent rounded-full focus:outline-none focus:border-gray-300 transition duration-150 ease-in-out w-11 h-11"
                                        style={{ minHeight: 'unset' }}
                                    >
                                        <div className="h-9 w-9 rounded-full bg-red-100 flex items-center justify-center text-red-600 font-bold border border-red-200">
                                            {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
                                        </div>
                                    </button>
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
                                                {[
                                                    { to: '/client/profile', icon: '👤', label: 'Profile' },
                                                    { to: '/client/orders', icon: '📦', label: 'Orders' },
                                                    { to: '/client/addresses', icon: '📍', label: 'Addresses' },
                                                    { to: '/client/favourites', icon: '❤️', label: 'Favourites' },
                                                    { to: '/client/wallet', icon: '👛', label: 'Wallet' },
                                                ].map(item => (
                                                    <Link
                                                        key={item.to}
                                                        to={item.to}
                                                        onClick={() => setIsMenuOpen(false)}
                                                        className="flex items-center w-full justify-start px-4 py-3 text-sm text-gray-700 hover:bg-red-50 hover:text-red-600 transition-all duration-200 no-tap-fix"
                                                        style={{ minHeight: 'unset' }}
                                                    >
                                                        <span className="mr-4 text-lg flex-shrink-0">{item.icon}</span> {item.label}
                                                    </Link>
                                                ))}
                                            </div>
                                            <div className="border-t border-gray-100 pt-2 pb-1">
                                                <Link
                                                    to="/client/help"
                                                    onClick={() => setIsMenuOpen(false)}
                                                    className="flex items-center w-full justify-start px-4 py-2.5 text-sm text-gray-600 hover:bg-gray-50 transition-all duration-200 italic no-tap-fix"
                                                    style={{ minHeight: 'unset' }}
                                                >
                                                    <span className="mr-4 text-lg flex-shrink-0">❓</span> Help & Support
                                                </Link>
                                                <button
                                                    onClick={() => { setIsMenuOpen(false); handleLogout(); }}
                                                    className="flex items-center w-full text-left px-4 py-3 text-sm text-red-600 hover:bg-red-50 transition-all duration-200 font-bold border-t border-gray-100 mt-2"
                                                    style={{ minHeight: 'unset' }}
                                                >
                                                    <span className="mr-4 text-lg">🚪</span> Logout
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <Link
                                    to="/login"
                                    className="bg-red-600 hover:bg-red-700 text-white px-4 sm:px-6 py-2 rounded-full text-sm font-bold transition-colors duration-200 shadow-md no-tap-fix"
                                    style={{ minHeight: 'unset' }}
                                >
                                    Login
                                </Link>
                            )}
                        </div>
                    </div>
                </div>
            </nav>

            {/* ===== MOBILE FULL-SCREEN SLIDE-IN DRAWER ===== */}
            {/* Backdrop */}
            {isDrawerOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-[100] sm:hidden"
                    onClick={() => setIsDrawerOpen(false)}
                />
            )}

            {/* Drawer Panel */}
            <div
                className={`fixed top-0 left-0 h-full w-72 max-w-[85vw] bg-white z-[101] shadow-2xl transform transition-transform duration-300 ease-in-out sm:hidden flex flex-col ${isDrawerOpen ? 'translate-x-0' : '-translate-x-full'}`}
            >
                {/* Drawer Header */}
                <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100 bg-red-600">
                    <h1 className="text-2xl font-extrabold text-white italic">Foodis</h1>
                    <button
                        onClick={() => setIsDrawerOpen(false)}
                        className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center text-white hover:bg-white/30 transition"
                        aria-label="Close menu"
                        style={{ minHeight: 'unset' }}
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* User info if logged in */}
                {user && (
                    <div className="flex items-center gap-3 px-5 py-4 bg-red-50 border-b border-red-100">
                        <div className="h-12 w-12 rounded-full bg-red-600 flex items-center justify-center text-white text-xl font-bold flex-shrink-0">
                            {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
                        </div>
                        <div className="min-w-0">
                            <p className="font-bold text-gray-900 truncate">{user.name}</p>
                            <p className="text-xs text-gray-500 truncate">{user.phone || user.email}</p>
                        </div>
                    </div>
                )}

                {/* Nav Links */}
                <nav className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
                    {navLinks.map((link) => (
                        <Link
                            key={link.path}
                            to={link.path}
                            className={`flex items-center gap-4 px-4 py-3 rounded-xl text-base font-bold transition-colors no-tap-fix ${location.pathname === link.path || (link.path !== '/client' && location.pathname.startsWith(link.path))
                                ? 'bg-red-50 text-red-600'
                                : 'text-gray-700 hover:bg-gray-50'
                            }`}
                            style={{ minHeight: 'unset' }}
                        >
                            <span className="text-xl">{link.icon}</span>
                            {link.name}
                        </Link>
                    ))}

                    {user && (
                        <>
                            <div className="border-t border-gray-100 my-2 pt-2">
                                {[
                                    { to: '/client/profile', icon: '👤', label: 'Profile' },
                                    { to: '/client/addresses', icon: '📍', label: 'Addresses' },
                                    { to: '/client/wallet', icon: '👛', label: 'Wallet' },
                                ].map(item => (
                                    <Link
                                        key={item.to}
                                        to={item.to}
                                        className="flex items-center gap-4 px-4 py-3 rounded-xl text-base font-bold text-gray-700 hover:bg-gray-50 transition-colors no-tap-fix"
                                        style={{ minHeight: 'unset' }}
                                    >
                                        <span className="text-xl">{item.icon}</span> {item.label}
                                    </Link>
                                ))}
                            </div>
                        </>
                    )}
                </nav>

                {/* Drawer Footer */}
                <div className="px-4 py-4 border-t border-gray-100">
                    {user ? (
                        <button
                            onClick={() => { setIsDrawerOpen(false); handleLogout(); }}
                            className="w-full flex items-center gap-4 px-4 py-3 rounded-xl text-red-600 font-bold hover:bg-red-50 transition"
                            style={{ minHeight: 'unset' }}
                        >
                            <span className="text-xl">🚪</span> Logout
                        </button>
                    ) : (
                        <Link
                            to="/login"
                            className="w-full flex items-center justify-center bg-red-600 text-white py-3 rounded-xl font-bold hover:bg-red-700 transition no-tap-fix"
                            style={{ minHeight: 'unset' }}
                        >
                            Login
                        </Link>
                    )}
                </div>
            </div>
        </>
    );
};

export default Navbar;
