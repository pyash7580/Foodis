import { API_BASE_URL } from '../../config';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area
} from 'recharts';

import RestaurantOrderDetailsModal from './RestaurantOrderDetailsModal';

const RestaurantDashboard = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [orders, setOrders] = useState([]);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('PENDING');
    const [viewOrder, setViewOrder] = useState(null);

    useEffect(() => {
        fetchDashboardData();
        const interval = setInterval(fetchDashboardData, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchDashboardData = async () => {
        try {
            const timestamp = new Date().getTime();
            const [ordersRes, summaryRes] = await Promise.all([
                axios.get(`${API_BASE_URL}/api/restaurant/orders/?_t=${timestamp}`),
                axios.get(`${API_BASE_URL}/api/restaurant/restaurant/summary/?_t=${timestamp}`)
            ]);
            // Safely handle paginated or flat response
            const orderData = ordersRes.data?.results ? ordersRes.data.results : (Array.isArray(ordersRes.data) ? ordersRes.data : []);
            setOrders(orderData);
            setStats(summaryRes.data);
            setLoading(false);
        } catch (error) {
            console.error("Dashboard fetch error", error);
            setLoading(false);
        }
    };

    const handleStatusUpdate = async (orderId, action) => {
        try {
            await axios.post(`${API_BASE_URL}/api/restaurant/orders/${orderId}/${action}/`);
            toast.success(`Order ${action}ed successfully`);
            fetchDashboardData();
        } catch (error) {
            console.error("Action failed", error);
            toast.error(`Failed to ${action} order`);
        }
    };

    const getStatusColor = (status) => {
        const colors = {
            PENDING: 'bg-yellow-100 text-yellow-800',
            CONFIRMED: 'bg-blue-100 text-blue-800',
            PREPARING: 'bg-purple-100 text-purple-800',
            READY: 'bg-indigo-100 text-indigo-800',
            PICKED_UP: 'bg-orange-100 text-orange-800',
            DELIVERED: 'bg-green-100 text-green-800',
            CANCELLED: 'bg-red-100 text-red-800',
        };
        return colors[status] || 'bg-gray-100';
    };

    if (loading) return (
        <div className="flex flex-col justify-center items-center h-screen bg-gray-50">
            <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-red-600 mb-4"></div>
            <p className="text-gray-600 font-medium">Loading Dashboard...</p>
        </div>
    );

    const filteredOrders = orders.filter(order => {
        if (activeTab === 'ALL') return true;
        if (activeTab === 'PENDING') return order.status === 'PENDING' || order.status === 'CONFIRMED';
        if (activeTab === 'ACTIVE') return ['PREPARING', 'READY', 'PICKED_UP', 'ASSIGNED'].includes(order.status);
        if (activeTab === 'COMPLETED') return ['DELIVERED', 'CANCELLED'].includes(order.status);
        return true;
    });

    return (
        <div className="min-h-screen bg-[#fcfcfc] flex">
            {/* Sidebar */}
            <aside className="w-64 bg-white border-r border-gray-100 hidden lg:flex flex-col sticky top-0 h-screen">
                <div className="p-6 border-b border-gray-50">
                    <h2 className="text-2xl font-black text-red-600 tracking-tighter">FOODIS<span className="text-gray-900">.Biz</span></h2>
                </div>
                <nav className="flex-grow p-4 space-y-2">
                    <Link to="/restaurant/dashboard" className="flex items-center space-x-3 p-3 bg-red-50 text-red-600 rounded-xl font-bold">
                        <span>📊</span> <span>Dashboard</span>
                    </Link>
                    <Link to="/restaurant/menu" className="flex items-center space-x-3 p-3 text-gray-500 hover:bg-gray-50 rounded-xl font-medium transition">
                        <span>🍔</span> <span>Menu Management</span>
                    </Link>
                    <Link to="/restaurant/earnings" className="flex items-center space-x-3 p-3 text-gray-500 hover:bg-gray-50 rounded-xl font-medium transition">
                        <span>💰</span> <span>Earnings & Reports</span>
                    </Link>
                    <Link to="/restaurant/profile" className="flex items-center space-x-3 p-3 text-gray-500 hover:bg-gray-50 rounded-xl font-medium transition">
                        <span>🏢</span> <span>Restaurant Profile</span>
                    </Link>
                </nav>
                <div className="p-4 border-t border-gray-50">
                    <button onClick={logout} className="flex items-center space-x-3 p-3 w-full text-red-400 hover:bg-red-50 rounded-xl font-medium transition">
                        <span>🚪</span> <span>Logout</span>
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-grow p-8">
                <header className="flex justify-between items-center mb-10">
                    <div>
                        <h1 className="text-3xl font-black text-gray-900">Good Morning, {stats?.restaurant?.name}!</h1>
                        <p className="text-gray-500 mt-1">Here's what's happening at your outlet today.</p>
                    </div>
                    <div className="flex items-center space-x-4">
                        <div className="bg-white p-2 px-4 rounded-full shadow-sm border border-gray-100 flex items-center space-x-2">
                            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                            <span className="text-sm font-bold text-gray-700 uppercase tracking-widest">Live Outlet</span>
                        </div>
                    </div>
                </header>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-50 h-32 flex flex-col justify-between">
                        <p className="text-gray-400 text-xs font-bold uppercase tracking-widest">Today's Revenue</p>
                        <p className="text-3xl font-black text-gray-900">₹{stats?.earnings?.today?.toLocaleString()}</p>
                    </div>
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-50 h-32 flex flex-col justify-between">
                        <p className="text-gray-400 text-xs font-bold uppercase tracking-widest">New Orders</p>
                        <p className="text-3xl font-black text-gray-900">{stats?.orders?.today}</p>
                    </div>
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-50 h-32 flex flex-col justify-between">
                        <p className="text-gray-400 text-xs font-bold uppercase tracking-widest">Pending</p>
                        <p className="text-3xl font-black text-yellow-500">{stats?.orders?.pending}</p>
                    </div>
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-50 h-32 flex flex-col justify-between bg-gradient-to-br from-red-500 to-red-600">
                        <p className="text-white text-xs font-bold uppercase tracking-widest opacity-80">Weekly Gross</p>
                        <p className="text-3xl font-black text-white">₹{stats?.earnings?.week?.toLocaleString()}</p>
                    </div>
                </div>

                <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-50 mb-10">
                    <div className="flex justify-between items-center mb-8">
                        <h2 className="text-xl font-black text-gray-900">Order Performance</h2>
                        <div className="flex space-x-4">
                            <span className="flex items-center space-x-1 text-xs font-bold text-gray-400">
                                <span className="w-3 h-3 bg-red-500 rounded-sm"></span>
                                <span>Revenue (₹)</span>
                            </span>
                            <span className="flex items-center space-x-1 text-xs font-bold text-gray-400">
                                <span className="w-3 h-3 bg-blue-500 rounded-sm"></span>
                                <span>Orders</span>
                            </span>
                        </div>
                    </div>
                    <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={stats?.graph_data}>
                                <defs>
                                    <linearGradient id="colorEarnings" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.1} />
                                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="colorOrders" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1} />
                                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fontWeight: 700, fill: '#9ca3af' }} dy={10} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fontWeight: 600, fill: '#9ca3af' }} />
                                <Tooltip
                                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                                    cursor={{ stroke: '#ef4444', strokeWidth: 2 }}
                                />
                                <Area type="monotone" dataKey="orders" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorOrders)" />
                                <Area type="monotone" dataKey="earnings" stroke="#ef4444" strokeWidth={4} fillOpacity={1} fill="url(#colorEarnings)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Orders Management */}
                <div className="space-y-6">
                    <div className="flex justify-between items-center">
                        <h2 className="text-2xl font-black text-gray-900">Live Orders</h2>
                        <div className="bg-gray-100 p-1 rounded-xl flex space-x-1">
                            {['PENDING', 'ACTIVE', 'COMPLETED', 'ALL'].map(tab => (
                                <button
                                    key={tab}
                                    onClick={() => setActiveTab(tab)}
                                    className={`px-4 py-2 text-xs font-bold rounded-lg transition ${activeTab === tab ? 'bg-white text-red-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                                >
                                    {tab.charAt(0) + tab.slice(1).toLowerCase()}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="grid grid-cols-1 gap-4">
                        {filteredOrders.length === 0 ? (
                            <div className="bg-white border-2 border-dashed border-gray-100 rounded-3xl py-20 text-center flex flex-col items-center">
                                <span className="text-5xl mb-4">🌮</span>
                                <h3 className="text-lg font-bold text-gray-900">Quiet for now...</h3>
                                <p className="text-gray-400">Incoming orders will appear here automatically.</p>
                            </div>
                        ) : (
                            filteredOrders.map(order => (
                                <div key={order.order_id} className="bg-white p-6 rounded-3xl shadow-sm border border-gray-50 flex flex-col md:flex-row md:items-center justify-between group hover:shadow-xl transition-all duration-300">
                                    <div className="flex items-center space-x-6">
                                        <div className="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center text-2xl group-hover:bg-red-50 transition">
                                            📦
                                        </div>
                                        <div>
                                            <div className="flex items-center space-x-3 mb-1">
                                                <h3 className="text-lg font-black text-gray-900">#{order.order_id}</h3>
                                                <span className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-widest ${getStatusColor(order.status)}`}>
                                                    {order.status}
                                                </span>
                                            </div>
                                            <p className="text-sm font-bold text-gray-400 uppercase tracking-tighter">
                                                {order.items.length} Items • ₹{order.total} • {new Date(order.placed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </p>

                                        </div>
                                    </div>

                                    {/* OTP Display */}
                                    {
                                        order.pickup_otp && (
                                            <div className="bg-red-50 px-4 py-2 rounded-xl border border-red-100 flex flex-col items-center justify-center mr-6">
                                                <span className="text-[10px] uppercase font-black text-red-400 tracking-widest">Pickup Code</span>
                                                <span className="text-xl font-black text-red-600 tracking-widest">{order.pickup_otp}</span>
                                            </div>
                                        )
                                    }

                                    < div className="flex items-center space-x-3 mt-4 md:mt-0" >
                                        {
                                            order.status === 'PENDING' && (
                                                <>
                                                    <button
                                                        onClick={() => handleStatusUpdate(order.order_id, 'reject')}
                                                        className="p-4 px-6 text-sm font-black text-red-500 hover:bg-red-50 rounded-2xl transition"
                                                    >
                                                        Reject
                                                    </button>
                                                    <button
                                                        onClick={() => handleStatusUpdate(order.order_id, 'accept')}
                                                        className="p-4 px-8 bg-red-600 text-white rounded-2xl font-black text-sm shadow-lg shadow-red-100 hover:bg-red-700 transition"
                                                    >
                                                        Accept Order
                                                    </button>
                                                </>
                                            )
                                        }
                                        {
                                            order.status === 'CONFIRMED' && (
                                                <button
                                                    onClick={() => handleStatusUpdate(order.order_id, 'start_preparing')}
                                                    className="p-4 px-8 bg-blue-600 text-white rounded-2xl font-black text-sm shadow-lg shadow-blue-100 hover:bg-blue-700 transition"
                                                >
                                                    Start Preparing
                                                </button>
                                            )
                                        }
                                        {
                                            order.status === 'PREPARING' && (
                                                <button
                                                    onClick={() => handleStatusUpdate(order.order_id, 'mark_ready')}
                                                    className="p-4 px-8 bg-indigo-600 text-white rounded-2xl font-black text-sm shadow-lg shadow-indigo-100 hover:bg-indigo-700 transition"
                                                >
                                                    Mark Ready
                                                </button>
                                            )
                                        }
                                        <button
                                            onClick={() => setViewOrder(order)}
                                            className="p-4 bg-gray-50 text-gray-400 rounded-2xl hover:bg-gray-100 transition"
                                        >
                                            <span>👁️</span>
                                        </button>
                                    </div>
                                </div>
                            ))
                        )}
                    </div >
                </div >
            </main>

            {/* Order Details Modal */}
            <RestaurantOrderDetailsModal
                order={viewOrder}
                onClose={() => setViewOrder(null)}
            />
        </div>
    );
};

export default RestaurantDashboard;
