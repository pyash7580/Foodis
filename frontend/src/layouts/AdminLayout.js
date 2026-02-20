
import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
    FaChartPie, FaUsers, FaUtensils, FaMotorcycle, FaShoppingBag,
    FaWallet, FaCommentAlt, FaCog, FaSignOutAlt, FaBars, FaTimes
} from 'react-icons/fa';

const AdminLayout = ({ children }) => {
    const { logout } = useAuth();
    const location = useLocation();
    const navigate = useNavigate();
    const [isSidebarOpen, setIsSidebarOpen] = React.useState(true);

    const menuItems = [
        { path: '/admin/dashboard', label: 'Dashboard', icon: <FaChartPie /> },
        { path: '/admin/users', label: 'User Management', icon: <FaUsers /> },
        { path: '/admin/restaurants', label: 'Restaurants', icon: <FaUtensils /> },
        { path: '/admin/riders', label: 'Riders', icon: <FaMotorcycle /> },
        { path: '/admin/orders', label: 'Orders', icon: <FaShoppingBag /> },
        { path: '/admin/finance', label: 'Finance & Refunds', icon: <FaWallet /> },
        { path: '/admin/reviews', label: 'Reviews & Ratings', icon: <FaCommentAlt /> },
        { path: '/admin/settings', label: 'System Settings', icon: <FaCog /> },
    ];

    const handleLogout = () => {
        logout();
        navigate('/admin/login');
    };

    return (
        <div className="flex h-screen bg-gray-100 overflow-hidden font-sans">
            {/* Sidebar */}
            <aside
                className={`bg-gray-900 text-white flex-shrink-0 transition-all duration-300 ${isSidebarOpen ? 'w-64' : 'w-20'
                    } flex flex-col`}
            >
                <div className="h-16 flex items-center justify-between px-4 bg-black">
                    {isSidebarOpen ? (
                        <h1 className="text-xl font-black tracking-widest text-[#FF4757] uppercase">FOODIS<span className="text-white text-xs block font-normal tracking-normal">Admin Panel</span></h1>
                    ) : (
                        <h1 className="text-xl font-black text-[#FF4757]">F</h1>
                    )}
                    <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="text-gray-400 hover:text-white">
                        {isSidebarOpen ? <FaTimes /> : <FaBars />}
                    </button>
                </div>

                <nav className="flex-1 overflow-y-auto py-6 space-y-2">
                    {menuItems.map((item) => {
                        const isActive = location.pathname.startsWith(item.path);
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`flex items-center px-4 py-3 mx-2 rounded-xl transition-all ${isActive
                                    ? 'bg-[#FF4757] text-white shadow-lg'
                                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                                    }`}
                                title={item.label}
                            >
                                <span className={`text-xl ${isSidebarOpen ? 'mr-3' : 'mx-auto'}`}>{item.icon}</span>
                                {isSidebarOpen && <span className="font-medium whitespace-nowrap">{item.label}</span>}
                            </Link>
                        );
                    })}
                </nav>

                <div className="p-4 border-t border-gray-800">
                    <button
                        onClick={handleLogout}
                        className={`w-full flex items-center ${isSidebarOpen ? 'justify-start' : 'justify-center'} px-4 py-3 text-red-400 hover:bg-gray-800 rounded-xl transition-colors`}
                    >
                        <FaSignOutAlt className="text-xl" />
                        {isSidebarOpen && <span className="ml-3 font-medium">Logout</span>}
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col overflow-hidden relative">
                {/* Header */}
                <header className="h-16 bg-white shadow-sm flex items-center justify-between px-8">
                    <h2 className="text-2xl font-bold text-gray-800">
                        {menuItems.find(m => location.pathname.startsWith(m.path))?.label || 'Overview'}
                    </h2>
                    <div className="flex items-center space-x-4">
                        <div className="text-right">
                            <p className="text-sm font-bold text-gray-800">Super Admin</p>
                            <span className="text-xs text-green-500 font-bold uppercase tracking-wider">● Online</span>
                        </div>
                        <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center font-bold text-gray-600">
                            A
                        </div>
                    </div>
                </header>

                {/* Content Scrollable Area */}
                <div className="flex-1 overflow-y-auto p-8">
                    {children}
                </div>
            </main>
        </div>
    );
};

export default AdminLayout;
