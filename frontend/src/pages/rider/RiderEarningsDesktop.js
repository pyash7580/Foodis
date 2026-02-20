import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../config';
import { useRider } from '../../contexts/RiderContext';
import { FaCalendarAlt, FaClock, FaChartLine, FaWallet, FaArrowUp } from 'react-icons/fa';
import { motion } from 'framer-motion';

const RiderEarningsDesktop = () => {
    const { headers } = useRider();
    const [earnings, setEarnings] = useState({
        today: 0,
        week: 0,
        month: 0,
        total_orders: 0
    });
    const [loading, setLoading] = useState(true);

    const fetchEarnings = useCallback(async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/api/rider/earnings/summary/`, { headers });
            setEarnings(res.data);
            setLoading(false);
        } catch (err) {
            console.error("Earnings fetch error", err);
            setLoading(false);
        }
    }, [headers]);

    useEffect(() => {
        fetchEarnings();
    }, [fetchEarnings]);

    if (loading) return (
        <div className="flex items-center justify-center h-full">
            <p className="text-2xl font-bold text-gray-400">Loading Earnings...</p>
        </div>
    );

    return (
        <div className="h-full p-8 space-y-8 overflow-auto relative">
            {/* Header Card */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card p-10 rounded-[2.5rem] relative overflow-hidden group"
            >
                <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/10 rounded-full blur-[100px] -mr-32 -mt-32 group-hover:bg-emerald-500/20 transition-all duration-700"></div>

                <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between">
                    <div>
                        <div className="flex items-center space-x-3 mb-4">
                            <div className="p-3 bg-emerald-500/20 rounded-2xl">
                                <FaWallet className="text-emerald-400 text-2xl" />
                            </div>
                            <h1 className="text-3xl font-black text-white tracking-tight">Earnings Finance</h1>
                        </div>
                        <p className="text-gray-400 font-bold uppercase text-[10px] tracking-[0.2em] ml-1">Live Revenue & Wallet Summary</p>
                    </div>

                    <div className="mt-8 md:mt-0 text-left md:text-right">
                        <p className="text-emerald-400 font-black uppercase text-xs tracking-widest mb-2">Available Balance</p>
                        <h2 className="text-6xl font-black text-white flex items-center md:justify-end">
                            <span className="text-3xl opacity-40 mr-2 font-light">₹</span>
                            {parseFloat(earnings.wallet_balance || 0).toLocaleString('en-IN')}
                        </h2>
                        <button className="mt-4 bg-[#FF3008] text-white px-8 py-3 rounded-xl font-black text-sm uppercase tracking-widest hover:bg-[#FF6B00] transition-all shadow-[0_10px_20px_rgba(255,48,8,0.3)] font-jakarta">
                            Request Payout
                        </button>
                    </div>
                </div>
            </motion.div>

            {/* Stats Grid */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="grid grid-cols-1 md:grid-cols-3 gap-8"
            >
                <div className="glass-card p-8 rounded-[2rem] border border-white/5">
                    <div className="flex items-center justify-between mb-6">
                        <div className="p-3 bg-blue-500/20 rounded-2xl">
                            <FaCalendarAlt className="text-blue-400 text-xl" />
                        </div>
                        <span className="text-[10px] font-black text-blue-400 bg-blue-400/10 px-3 py-1 rounded-full">THIS WEEK</span>
                    </div>
                    <p className="text-xs text-gray-500 font-black uppercase tracking-widest mb-1">Weekly Revenue</p>
                    <h3 className="text-4xl font-black text-white">₹{earnings.week}</h3>
                </div>

                <div className="glass-card p-8 rounded-[2rem] border border-white/5">
                    <div className="flex items-center justify-between mb-6">
                        <div className="p-3 bg-purple-500/20 rounded-2xl">
                            <FaClock className="text-purple-400 text-xl" />
                        </div>
                        <span className="text-[10px] font-black text-purple-400 bg-purple-400/10 px-3 py-1 rounded-full">THIS MONTH</span>
                    </div>
                    <p className="text-xs text-gray-500 font-black uppercase tracking-widest mb-1">Monthly Revenue</p>
                    <h3 className="text-4xl font-black text-white">₹{earnings.month}</h3>
                </div>

                <div className="glass-card p-8 rounded-[2rem] border border-white/5">
                    <div className="flex items-center justify-between mb-6">
                        <div className="p-3 bg-orange-500/20 rounded-2xl">
                            <FaChartLine className="text-orange-400 text-xl" />
                        </div>
                        <span className="text-[10px] font-black text-orange-400 bg-orange-400/10 px-3 py-1 rounded-full">LIFETIME</span>
                    </div>
                    <p className="text-xs text-gray-500 font-black uppercase tracking-widest mb-1">Total Deliveries</p>
                    <h3 className="text-4xl font-black text-white">{earnings.total_orders}</h3>
                </div>
            </motion.div>

            {/* Performance Analytics */}
            <motion.div
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="glass-morphism-dark p-10 rounded-[2.5rem] border border-white/10 shadow-2xl"
            >
                <div className="flex items-center justify-between mb-8">
                    <h3 className="text-2xl font-black text-white tracking-tight">Earnings Analytics</h3>
                    <div className="flex space-x-2">
                        <button className="px-4 py-2 rounded-lg bg-white/10 text-xs font-black text-white border border-white/10 uppercase">Export PDF</button>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                    <div className="space-y-6">
                        <div className="flex justify-between items-center p-6 bg-white/5 rounded-[1.5rem] border border-white/5 hover:bg-white/10 transition-colors">
                            <div>
                                <p className="text-xs font-black text-gray-500 uppercase tracking-widest mb-1">Average Pay / Trip</p>
                                <p className="text-2xl font-black text-white">
                                    ₹{earnings.total_orders > 0 ? (earnings.month / earnings.total_orders).toFixed(0) : '0'}
                                </p>
                            </div>
                            <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                                <FaArrowUp className="text-emerald-400 text-sm" />
                            </div>
                        </div>

                        <div className="flex justify-between items-center p-6 bg-white/5 rounded-[1.5rem] border border-white/5 hover:bg-white/10 transition-colors">
                            <div>
                                <p className="text-xs font-black text-gray-500 uppercase tracking-widest mb-1">Success Rate</p>
                                <p className="text-2xl font-black text-white">98.4%</p>
                            </div>
                            <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
                                <FaChartLine className="text-blue-400 text-sm" />
                            </div>
                        </div>
                    </div>

                    <div className="bg-gradient-to-br from-[#1A1A1A] to-[#0A0A0A] p-8 rounded-[1.5rem] border border-white/5 flex flex-col justify-center text-center">
                        <p className="text-[10px] text-emerald-400 font-black uppercase tracking-[0.3em] mb-4">Projected Earnings</p>
                        <h4 className="text-5xl font-black text-white mb-2">₹{(earnings.today * 30).toLocaleString()}</h4>
                        <p className="text-xs text-gray-500 font-bold uppercase">Estimated next 30 days based on today's perf.</p>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default RiderEarningsDesktop;
