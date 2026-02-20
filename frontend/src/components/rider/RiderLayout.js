
import React from 'react';
import { NavLink, useNavigate, Outlet } from 'react-router-dom';
import { FaHome, FaWallet, FaUser, FaMotorcycle, FaSignOutAlt, FaPowerOff, FaTrophy, FaBell, FaBox } from 'react-icons/fa';
import { useAuth } from '../../contexts/AuthContext';
import { useRider } from '../../contexts/RiderContext';

const RiderLayout = () => {
    const navigate = useNavigate();
    const { logout } = useAuth();
    const { isOnline, profile, toggleOnline } = useRider();

    const handleLogout = () => {
        logout();
        navigate('/rider/login');
    };

    const navItems = [
        { path: '/rider/dashboard', icon: FaHome, label: 'Dashboard' },
        { path: '/rider/orders', icon: FaBox, label: 'Orders' },
        { path: '/rider/missions', icon: FaTrophy, label: 'Missions' },
        { path: '/rider/earnings', icon: FaWallet, label: 'Earnings' },
        { path: '/rider/profile', icon: FaUser, label: 'Profile' }
    ];

    return (
        <div className="layout">
            <aside className="sidebar flex flex-col items-stretch">
                {/* Branding Section */}
                <div className="p-8 border-b border-white/5">
                    <div className="flex items-center space-x-4 mb-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#FF3008] to-[#FF6B00] flex items-center justify-center shadow-lg text-white">
                            <FaMotorcycle className="text-2xl" />
                        </div>
                        <div>
                            <h1 className="text-xl font-black tracking-tighter text-white">FOODIS</h1>
                            <p className="text-[8px] text-gray-400 font-bold uppercase tracking-[0.2em]">Partner</p>
                        </div>
                    </div>
                </div>

                {/* Duty Toggle Section */}
                <div className="px-6 py-8">
                    <button
                        onClick={toggleOnline}
                        className={`w-full flex items-center justify-between p-4 rounded-xl transition-all duration-300 ${isOnline
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.1)]'
                            : 'bg-white/5 text-gray-400 border border-white/5 hover:bg-white/10'
                            }`}
                    >
                        <div className="flex items-center space-x-3">
                            <div className={`p-2 rounded-lg ${isOnline ? 'bg-emerald-500/20' : 'bg-gray-800'}`}>
                                <FaPowerOff className={`text-sm ${isOnline ? 'animate-pulse' : ''}`} />
                            </div>
                            <span className="font-black text-xs uppercase tracking-wider">{isOnline ? 'Active' : 'Offline'}</span>
                        </div>
                        <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-500 shadow-[0_0_8px_#10B981]' : 'bg-gray-600'}`}></div>
                    </button>
                </div>

                {/* Navigation Section */}
                <nav className="flex-1 px-4 space-y-1">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                `flex items-center space-x-4 p-3 rounded-xl transition-all duration-300 ${isActive
                                    ? 'bg-white/10 text-white border border-white/5'
                                    : 'text-gray-400 hover:text-white hover:bg-white/5'}`
                            }
                        >
                            <item.icon className="text-lg opacity-80" />
                            <span className="font-bold text-xs uppercase tracking-wide">{item.label}</span>
                        </NavLink>
                    ))}
                </nav>

                {/* Logout Section */}
                <div className="p-6 border-t border-white/5">
                    <button
                        onClick={handleLogout}
                        className="w-full flex items-center space-x-3 p-3 rounded-xl text-gray-500 hover:text-red-400 hover:bg-red-500/10 transition-all duration-300"
                    >
                        <FaSignOutAlt className="text-lg" />
                        <span className="font-bold text-xs uppercase tracking-wide">Logout</span>
                    </button>
                </div>
            </aside>
            <main className="content flex flex-col">
                {/* Global Header */}
                <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-[#0f172a]/50 backdrop-blur-md sticky top-0 z-10 w-full">
                    <div>
                        <h2 className="text-lg font-black text-white tracking-widest uppercase opacity-80">Rider Dashboard</h2>
                    </div>

                    <div className="flex items-center space-x-6">
                        <button className="p-2.5 bg-white/5 rounded-xl border border-white/5 text-gray-400 hover:text-white transition-all relative">
                            <FaBell className="text-lg" />
                            <span className="absolute top-2 right-2 w-1.5 h-1.5 bg-[#FF3008] rounded-full"></span>
                        </button>

                        <div className="h-8 w-px bg-white/10"></div>

                        <div className="flex items-center space-x-3">
                            <div className="text-right hidden sm:block">
                                <p className="text-[10px] font-black text-white uppercase tracking-tight">{profile?.rider_name || 'Rider'}</p>
                                <p className="text-[8px] text-gray-500 font-bold uppercase">ID: {profile?.id || '...'}</p>
                            </div>
                            <div className="w-9 h-9 rounded-lg bg-gray-800 border border-white/5 flex items-center justify-center text-gray-400 font-black text-xs uppercase overflow-hidden ring-2 ring-white/5">
                                {profile?.rider_name?.[0] || 'R'}
                            </div>
                        </div>
                    </div>
                </header>

                <div className="flex-1 p-8">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};

export default RiderLayout;

