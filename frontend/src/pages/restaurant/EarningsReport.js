import { API_BASE_URL } from '../../config';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../../contexts/AuthContext';
import {
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area
} from 'recharts';

const EarningsReport = () => {
    const { logout } = useAuth();
    const [earnings, setEarnings] = useState([]);
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const timestamp = new Date().getTime();
            const [earningsRes, summaryRes] = await Promise.all([
                axios.get(`${API_BASE_URL}/api/restaurant/earnings/?_t=${timestamp}`),
                axios.get(`${API_BASE_URL}/api/restaurant/earnings/summary/?_t=${timestamp}`)
            ]);
            // Safely handle paginated or flat response
            const earningsData = earningsRes.data?.results ? earningsRes.data.results : (Array.isArray(earningsRes.data) ? earningsRes.data : []);
            setEarnings(earningsData);
            setSummary(summaryRes.data);
            setLoading(false);
        } catch (error) {
            console.error("Fetch error", error);
            toast.error("Failed to load earnings data");
            setLoading(false);
        }
    };

    const handleDownload = () => {
        window.open(`${API_BASE_URL}/api/restaurant/earnings/download_csv/`, '_blank');
        toast.success("Statement download started");
    };

    if (loading) return <div className="p-8 text-center text-gray-500 font-bold">Calculating Earnings...</div>;

    const graphData = [...earnings].reverse().map(e => ({
        name: new Date(e.date).toLocaleDateString([], { day: 'numeric', month: 'short' }),
        amount: parseFloat(e.net_amount)
    }));

    return (
        <div className="min-h-screen bg-[#fcfcfc] flex">
            <aside className="w-64 bg-white border-r border-gray-100 hidden lg:flex flex-col sticky top-0 h-screen">
                <div className="p-6 border-b border-gray-50">
                    <h2 className="text-2xl font-black text-red-600 tracking-tighter">FOODIS<span className="text-gray-900">.Biz</span></h2>
                </div>
                <nav className="flex-grow p-4 space-y-2">
                    <Link to="/restaurant/dashboard" className="flex items-center space-x-3 p-3 text-gray-500 hover:bg-gray-50 rounded-xl font-medium transition">
                        <span>📊</span> <span>Dashboard</span>
                    </Link>
                    <Link to="/restaurant/menu" className="flex items-center space-x-3 p-3 text-gray-500 hover:bg-gray-50 rounded-xl font-medium transition">
                        <span>🍔</span> <span>Menu Management</span>
                    </Link>
                    <Link to="/restaurant/earnings" className="flex items-center space-x-3 p-3 bg-red-50 text-red-600 rounded-xl font-bold">
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

            <main className="flex-grow w-full min-w-0 p-4 md:p-8 pb-28 md:pb-8">
                <header className="flex flex-col md:flex-row md:justify-between items-start md:items-center gap-4 mb-10">
                    <div>
                        <h1 className="text-3xl font-black text-gray-900">Earnings & Reports</h1>
                        <p className="text-gray-500 mt-1">Detailed breakdown of your revenue and payouts.</p>
                    </div>
                    <button
                        onClick={handleDownload}
                        className="bg-black text-white px-6 py-3 rounded-2xl font-bold flex items-center space-x-2 shadow-lg hover:bg-gray-800 transition"
                    >
                        <span>📥</span> <span>Download Statement (CSV)</span>
                    </button>
                </header>

                <div className="grid grid-cols-3 md:grid-cols-3 gap-2 md:gap-6 mb-8 md:mb-10">
                    <div className="bg-white p-3 md:p-6 rounded-xl md:rounded-2xl shadow-sm border border-gray-50 flex flex-col justify-center">
                        <p className="text-gray-400 text-[8px] md:text-xs font-bold uppercase tracking-widest mb-1 truncate">Today</p>
                        <p className="text-lg md:text-3xl font-black text-gray-900 truncate">₹{summary?.today?.toLocaleString()}</p>
                    </div>
                    <div className="bg-white p-3 md:p-6 rounded-xl md:rounded-2xl shadow-sm border border-gray-50 flex flex-col justify-center">
                        <p className="text-gray-400 text-[8px] md:text-xs font-bold uppercase tracking-widest mb-1 truncate">7 Days</p>
                        <p className="text-lg md:text-3xl font-black text-gray-900 truncate">₹{summary?.week?.toLocaleString()}</p>
                    </div>
                    <div className="bg-white p-3 md:p-6 rounded-xl md:rounded-2xl shadow-sm border border-gray-50 flex flex-col justify-center">
                        <p className="text-gray-400 text-[8px] md:text-xs font-bold uppercase tracking-widest mb-1 truncate">30 Days</p>
                        <p className="text-lg md:text-3xl font-black text-gray-900 truncate">₹{summary?.month?.toLocaleString()}</p>
                    </div>
                </div>

                <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-50 mb-10">
                    <h2 className="text-xl font-black text-gray-900 mb-8">Revenue Trend</h2>
                    <div className="h-72 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={graphData}>
                                <defs>
                                    <linearGradient id="colorAmount" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.1} />
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fontWeight: 700, fill: '#9ca3af' }} />
                                <YAxis hide />
                                <Tooltip
                                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                                />
                                <Area type="monotone" dataKey="amount" stroke="#10b981" strokeWidth={4} fillOpacity={1} fill="url(#colorAmount)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="bg-white rounded-3xl shadow-sm border border-gray-50 overflow-hidden">
                    <div className="p-5 md:p-8 border-b border-gray-50">
                        <h2 className="text-xl font-black text-gray-900">Transaction History</h2>
                    </div>
                    <div className="overflow-x-auto w-full">
                        <table className="w-full text-left min-w-[600px]">
                            <thead>
                                <tr className="bg-gray-50 text-gray-400 text-[10px] font-black uppercase tracking-widest">
                                    <th className="px-5 md:px-8 py-4">Date</th>
                                    <th className="px-5 md:px-8 py-4">Order ID</th>
                                    <th className="px-5 md:px-8 py-4 text-right">Order Total</th>
                                    <th className="px-5 md:px-8 py-4 text-right text-red-400">Commission</th>
                                    <th className="px-5 md:px-8 py-4 text-right">Net Payout</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-50 text-sm font-medium text-gray-700">
                                {earnings.map(record => (
                                    <tr key={record.id} className="hover:bg-gray-50/50 transition">
                                        <td className="px-5 md:px-8 py-4 md:py-6 whitespace-nowrap">{new Date(record.date).toLocaleDateString([], { day: 'numeric', month: 'short', year: 'numeric' })}</td>
                                        <td className="px-5 md:px-8 py-4 md:py-6 font-bold whitespace-nowrap">#{record.order_id}</td>
                                        <td className="px-5 md:px-8 py-4 md:py-6 text-right whitespace-nowrap">₹{record.order_total}</td>
                                        <td className="px-5 md:px-8 py-4 md:py-6 text-right text-red-500 whitespace-nowrap">-₹{record.commission}</td>
                                        <td className="px-5 md:px-8 py-4 md:py-6 text-right font-black text-gray-900 whitespace-nowrap">₹{record.net_amount}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </main>

            {/* Mobile Bottom Navigation */}
            <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 flex justify-around items-center p-3 z-50 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] pb-6 md:pb-3">
                <Link to="/restaurant/dashboard" className={`flex flex-col items-center p-2 rounded-xl text-gray-400`}>
                    <span className="text-xl mb-1">📊</span>
                    <span className="text-[10px] font-bold">Dashboard</span>
                </Link>
                <Link to="/restaurant/menu" className={`flex flex-col items-center p-2 rounded-xl text-gray-400`}>
                    <span className="text-xl mb-1">🍔</span>
                    <span className="text-[10px] font-bold">Menu</span>
                </Link>
                <Link to="/restaurant/earnings" className={`flex flex-col items-center p-2 rounded-xl text-red-600`}>
                    <span className="text-xl mb-1">💰</span>
                    <span className="text-[10px] font-bold">Earnings</span>
                </Link>
                <Link to="/restaurant/profile" className={`flex flex-col items-center p-2 rounded-xl text-gray-400`}>
                    <span className="text-xl mb-1">🏢</span>
                    <span className="text-[10px] font-bold">Profile</span>
                </Link>
            </div>
        </div>
    );
};

export default EarningsReport;
