import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { FaHome, FaWallet, FaUser, FaMotorcycle, FaSignOutAlt, FaPowerOff, FaTrophy, FaClipboardList } from 'react-icons/fa';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import { useRider } from '../../contexts/RiderContext';

const RiderLayout = ({ children }) => {
    const { logout } = useAuth();
    const { isOnline, profile, toggleOnline, activeOrder } = useRider();

    const handleLogout = () => {
        logout();
    };

    const navItems = [
        { path: '/rider/dashboard', icon: FaHome, label: 'Home' },
        ...(activeOrder ? [{ path: `/rider/order/${activeOrder.id || activeOrder}`, icon: FaMotorcycle, label: 'Active Mission' }] : []),
        { path: '/rider/orders', icon: FaClipboardList, label: 'Orders' },
        { path: '/rider/earnings', icon: FaWallet, label: 'Earnings' },
        { path: '/rider/incentives', icon: FaTrophy, label: 'Incentives' },
        { path: '/rider/profile', icon: FaUser, label: 'Profile' }
    ];

    return (
        <div className="flex h-screen bg-[#0F172A] text-white overflow-hidden relative font-jakarta">
            {/* Background Decorative Blobs */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-red-600/10 rounded-full blur-[120px] animate-pulse"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-600/10 rounded-full blur-[120px] animate-pulse animation-delay-2000"></div>
            </div>

            {/* Desktop Sidebar */}
            <motion.aside
                initial={{ x: -100, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                className="hidden md:flex w-80 h-[calc(100vh-2rem)] m-4 glass-morphism-dark rounded-[2.5rem] shadow-2xl flex flex-col z-10 border border-white/5"
            >
                {/* Branding Section */}
                <div className="p-8 border-b border-white/5">
                    <div className="flex items-center space-x-4 mb-8">
                        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-[#FF3008] to-[#FF6B00] flex items-center justify-center shadow-[0_0_20px_rgba(255,48,8,0.3)] transform -rotate-3">
                            <FaMotorcycle className="text-white text-3xl" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-black tracking-tighter text-white">FOODIS</h1>
                            <p className="text-[10px] text-gray-400 font-bold uppercase tracking-[0.2em]">Rider Partner</p>
                        </div>
                    </div>

                    <div className="bg-white/5 rounded-2xl p-4 border border-white/5 flex items-center space-x-4">
                        <div className="w-10 h-10 rounded-full bg-gray-800 border-2 border-white/10 overflow-hidden flex items-center justify-center text-xl font-black text-gray-500 uppercase">
                            {profile?.rider_name?.[0] || 'R'}
                        </div>
                        <div className="flex-1 overflow-hidden">
                            <p className="text-sm font-black truncate">{profile?.rider_name || 'Rider Partner'}</p>
                            <div className="flex items-center text-[10px] text-gray-400 font-bold">
                                <span className={`px-2 py-0.5 rounded-full mr-2 ${profile?.is_online ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                    {profile?.is_online ? 'ACTIVE' : 'OFFLINE'}
                                </span>
                                {profile?.city || 'Himmatnagar'}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Duty Toggle Section */}
                <div className="px-8 py-6">
                    <button
                        onClick={toggleOnline}
                        className={`w-full group relative overflow-hidden flex items-center justify-between p-5 rounded-2xl transition-all duration-500 ${isOnline
                            ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-[0_10px_25px_rgba(16,185,129,0.3)]'
                            : 'bg-white/5 text-gray-400 border border-white/5 hover:bg-white/10'
                            }`}
                    >
                        <div className="flex items-center space-x-4 relative z-10">
                            <div className={`p-2 rounded-lg ${isOnline ? 'bg-white/20' : 'bg-gray-800'}`}>
                                <FaPowerOff className={`text-xl ${isOnline ? 'animate-pulse' : ''}`} />
                            </div>
                            <div className="text-left">
                                <p className="font-black text-sm uppercase tracking-wider">{isOnline ? 'Active' : 'Offline'}</p>
                                <p className="text-[9px] font-bold opacity-60 uppercase">{isOnline ? 'Ready for orders' : 'Not on duty'}</p>
                            </div>
                        </div>
                        <div className={`w-3 h-3 rounded-full relative z-10 ${isOnline ? 'bg-white shadow-[0_0_10px_#fff]' : 'bg-gray-600'}`}></div>
                    </button>
                </div>

                {/* Navigation Section */}
                <nav className="flex-1 px-8 space-y-3 overflow-y-auto scrollbar-hide">
                    <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest mb-2 ml-2">Main Menu</p>
                    {navItems.map((item) => (
                        <NavLink key={item.path} to={item.path} className={({ isActive }) =>
                            `group flex items-center space-x-4 p-4 rounded-2xl transition-all duration-300 relative ${isActive
                                ? 'bg-white/10 text-white shadow-xl border border-white/10'
                                : 'text-gray-400 hover:text-white hover:bg-white/5'}`
                        }>
                            {({ isActive }) => (
                                <>
                                    <div className={`p-2 rounded-xl transition-colors ${isActive ? 'bg-gradient-to-br from-[#FF3008] to-[#FF6B00] text-white' : 'bg-gray-800 text-gray-500 group-hover:text-gray-300'}`}>
                                        <item.icon className="text-xl" />
                                    </div>
                                    <span className="font-bold text-sm uppercase tracking-wide">{item.label}</span>
                                    {isActive && (
                                        <motion.div
                                            layoutId="activeTab"
                                            className="absolute left-[-1px] w-1.5 h-8 bg-[#FF3008] rounded-r-full shadow-[2px_0_10px_rgba(255,48,8,0.5)]"
                                        />
                                    )}
                                </>
                            )}
                        </NavLink>
                    ))}
                </nav>

                {/* User Settings & Logout */}
                <div className="p-8 border-t border-white/5">
                    <button
                        onClick={handleLogout}
                        className="w-full flex items-center space-x-4 p-4 rounded-2xl text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition-all duration-300 border border-transparent hover:border-red-500/20"
                    >
                        <div className="p-2 bg-gray-800 rounded-xl">
                            <FaSignOutAlt className="text-xl" />
                        </div>
                        <span className="font-bold text-sm uppercase tracking-wide">Logout Account</span>
                    </button>
                </div>
            </motion.aside>

            {/* Main Content Area */}
            <main className="flex-1 h-screen overflow-hidden relative flex flex-col z-10">
                <div className="flex-1 overflow-auto scrollbar-hide pb-24 md:pb-0">
                    {children || <Outlet />}
                </div>

                {/* Mobile Bottom Navigation */}
                <motion.div
                    initial={{ y: 100 }}
                    animate={{ y: 0 }}
                    className="md:hidden fixed bottom-6 left-6 right-6 z-[1000] glass-morphism-dark rounded-[2rem] border border-white/10 px-8 py-5 flex justify-between items-center shadow-2xl"
                >
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                `flex flex-col items-center space-y-1 transition-all duration-300 ${isActive ? 'text-[#FF3008] scale-125' : 'text-gray-500 opacity-60'}`
                            }
                        >
                            <item.icon className="text-2xl" />
                            <AnimatePresence>
                                {window.location.pathname === item.path && (
                                    <motion.div
                                        initial={{ scale: 0 }}
                                        animate={{ scale: 1 }}
                                        exit={{ scale: 0 }}
                                        className="w-1.5 h-1.5 bg-[#FF3008] rounded-full shadow-[0_0_8px_#FF3008]"
                                    />
                                )}
                            </AnimatePresence>
                        </NavLink>
                    ))}
                </motion.div>
            </main>
        </div>
    );
};

export default RiderLayout;
