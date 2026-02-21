import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../config';
import { FaChartLine, FaChevronLeft, FaHistory, FaArrowDown, FaMotorcycle } from 'react-icons/fa';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const RiderEarnings = () => {
    const navigate = useNavigate();
    const [earnings, setEarnings] = useState({
        today: 0,
        week: 0,
        month: 0,
        total_orders: 0,
        wallet_balance: 0
    });
    const [dailyOrders, setDailyOrders] = useState([]);
    const [loading, setLoading] = useState(true);

    const headers = useMemo(() => {
        const token = localStorage.getItem('token_rider');
        return { Authorization: `Bearer ${token}`, 'X-Role': 'RIDER' };
    }, []);

    const fetchEarnings = useCallback(async () => {
        try {
            const timestamp = new Date().getTime();
            const [summaryRes, dailyRes] = await Promise.all([
                axios.get(`${API_BASE_URL}/api/rider/earnings/summary/?_t=${timestamp}`, { headers }),
                axios.get(`${API_BASE_URL}/api/rider/earnings/daily_breakdown/?_t=${timestamp}`, { headers })
            ]);
            setEarnings(summaryRes.data);
            setDailyOrders(dailyRes.data);
            setLoading(false);
        } catch (err) {
            console.error("Earnings fetch error", err);
            setLoading(false);
        }
    }, [headers]);

    useEffect(() => {
        fetchEarnings();
    }, [fetchEarnings]);

    if (loading) return <div className="p-10 text-center font-bold text-gray-400">Loading Earnings...</div>;

    return (
        <div className="min-h-screen bg-[#0F172A] pb-24 font-jakarta text-white relative overflow-hidden">
            {/* Background Decorative Blobs */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
                <div className="absolute top-[-10%] right-[-10%] w-[60%] h-[40%] bg-emerald-600/10 rounded-full blur-[100px]"></div>
                <div className="absolute bottom-[-10%] left-[-10%] w-[60%] h-[40%] bg-blue-600/10 rounded-full blur-[100px]"></div>
            </div>

            {/* Header / Wallet Section */}
            <div className="glass-morphism-dark p-8 rounded-b-[3.5rem] shadow-[0_20px_50px_rgba(0,0,0,0.5)] relative z-10 border-b border-white/5">
                <div className="relative z-10">
                    <div className="flex justify-between items-center mb-10">
                        <button onClick={() => navigate(-1)} className="p-3 bg-white/5 rounded-2xl border border-white/5 text-white/70">
                            <FaChevronLeft className="text-xl" />
                        </button>
                        <h1 className="text-sm font-black tracking-[0.2em] uppercase text-gray-400">Finance Center</h1>
                        <div className="w-12"></div>
                    </div>

                    <p className="text-emerald-400 font-black uppercase text-[10px] tracking-[0.3em] text-center mb-2">Available Balance</p>
                    <h2 className="text-6xl font-black flex items-center justify-center text-white tracking-tighter">
                        <span className="text-2xl opacity-40 mr-2 font-light">₹</span>
                        {parseFloat(earnings.wallet_balance).toLocaleString('en-IN')}
                    </h2>

                    <div className="grid grid-cols-2 gap-4 mt-12">
                        <button className="bg-[#FF3008] text-white p-5 rounded-3xl flex items-center justify-center space-x-3 shadow-[0_15px_30px_rgba(255,48,8,0.3)] transition-all active:scale-95 border border-white/10">
                            <FaArrowDown className="text-lg" />
                            <span className="text-[10px] font-black uppercase tracking-widest">Withdraw</span>
                        </button>
                        <button className="bg-white/5 text-gray-300 p-5 rounded-3xl flex items-center justify-center space-x-3 border border-white/5 transition-all active:scale-95">
                            <FaHistory className="text-lg" />
                            <span className="text-[10px] font-black uppercase tracking-widest">History</span>
                        </button>
                    </div>
                </div>
            </div>

            <div className="p-8 relative z-10">
                {/* Stats Row */}
                <div className="grid grid-cols-2 gap-4 mb-10">
                    <motion.div
                        whileTap={{ scale: 0.95 }}
                        className="glass-card p-6 rounded-[2rem] border border-white/5"
                    >
                        <div className="p-2 bg-blue-500/20 w-fit rounded-lg mb-4">
                            <FaChartLine className="text-blue-400 text-sm" />
                        </div>
                        <p className="text-gray-500 text-[9px] font-black uppercase tracking-[0.2em] mb-1">Today's Pay</p>
                        <p className="text-2xl font-black text-white">₹{earnings.today}</p>
                    </motion.div>
                    <motion.div
                        whileTap={{ scale: 0.95 }}
                        className="glass-card p-6 rounded-[2rem] border border-white/5"
                    >
                        <div className="p-2 bg-purple-500/20 w-fit rounded-lg mb-4">
                            <FaMotorcycle className="text-purple-400 text-sm" />
                        </div>
                        <p className="text-gray-500 text-[9px] font-black uppercase tracking-[0.2em] mb-1">Total Trips</p>
                        <p className="text-2xl font-black text-white">{earnings.total_orders}</p>
                    </motion.div>
                </div>

                <div className="flex justify-between items-end mb-8">
                    <div>
                        <h3 className="font-black text-white text-2xl tracking-tight">Today's Work</h3>
                        <p className="text-[8px] text-gray-500 font-black uppercase tracking-widest mt-1">Live Transaction Log</p>
                    </div>
                    <span className="text-emerald-400 text-[10px] font-black uppercase tracking-widest bg-emerald-400/10 px-4 py-2 rounded-full">LIVE</span>
                </div>

                <div className="space-y-4">
                    {dailyOrders.length === 0 ? (
                        <div className="text-center py-20 grayscale opacity-20 bg-white/5 rounded-[2.5rem] border border-white/5 border-dashed">
                            <FaMotorcycle className="text-6xl mx-auto mb-6" />
                            <p className="font-black text-sm uppercase tracking-widest">No deliveries yet</p>
                        </div>
                    ) : (
                        dailyOrders.map((order) => (
                            <motion.div
                                key={order.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="flex items-center justify-between p-5 glass-card rounded-[1.8rem] border border-white/5"
                            >
                                <div className="flex items-center space-x-5">
                                    <div className="w-14 h-14 bg-white/5 rounded-2xl flex items-center justify-center border border-white/5">
                                        <FaMotorcycle className="text-red-500 text-xl" />
                                    </div>
                                    <div>
                                        <p className="font-black text-white text-sm">Order #{order.order_id}</p>
                                        <div className="flex items-center space-x-2 mt-1">
                                            <span className="text-[9px] text-gray-500 font-bold uppercase truncate max-w-[100px]">{order.restaurant_name}</span>
                                            <span className="w-1 h-1 bg-gray-700 rounded-full"></span>
                                            <span className="text-[9px] text-gray-500 font-bold uppercase">{new Date(order.placed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="font-black text-emerald-400 text-lg">₹{order.total}</p>
                                    <p className="text-[8px] text-gray-600 font-black uppercase tracking-widest">Credit</p>
                                </div>
                            </motion.div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default RiderEarnings;
