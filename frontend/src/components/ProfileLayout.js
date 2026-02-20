
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import Navbar from './Navbar';

const ProfileLayout = ({ children }) => {
    const location = useLocation();

    const menuItems = [
        { name: 'Profile', path: '/client/profile', icon: '👤' },
        { name: 'Orders', path: '/client/orders', icon: '📦' },
        { name: 'Addresses', path: '/client/addresses', icon: '📍' },
        { name: 'Favourites', path: '/client/favourites', icon: '❤️' },
        { name: 'Wallet', path: '/client/wallet', icon: '👛' },
        { name: 'Help', path: '/client/help', icon: '❓' },
    ];

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            <Navbar />
            <div className="flex-1 max-w-[1600px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="flex flex-col md:flex-row gap-8">
                    {/* Sidebar */}
                    <div className="w-full md:w-64 flex-shrink-0">
                        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden sticky top-24">
                            <nav className="flex flex-col">
                                {menuItems.map((item) => {
                                    const isActive = location.pathname === item.path;
                                    return (
                                        <Link
                                            key={item.name}
                                            to={item.path}
                                            className={`flex items-center px-6 py-4 text-sm font-semibold transition-all duration-200 ${isActive
                                                ? 'bg-red-50 text-red-600 border-r-4 border-red-600'
                                                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 border-r-4 border-transparent'
                                                }`}
                                        >
                                            <span className="mr-4 text-xl">{item.icon}</span>
                                            {item.name}
                                        </Link>
                                    );
                                })}
                            </nav>
                        </div>
                    </div>

                    {/* Main Content */}
                    <div className="flex-1">
                        {children}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProfileLayout;
