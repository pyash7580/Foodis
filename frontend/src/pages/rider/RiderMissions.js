import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { FaTrophy, FaRupeeSign, FaCheckCircle, FaClock, FaFire, FaChartLine } from 'react-icons/fa';
import { API_BASE_URL } from '../../config';
import { useRider } from '../../contexts/RiderContext';

const RiderMissions = () => {
    const { headers } = useRider();
    const [incentives, setIncentives] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchIncentives = useCallback(async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/api/rider/incentives/progress/`, { headers });
            setIncentives(res.data);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    }, [headers]);

    useEffect(() => {
        fetchIncentives();
    }, [fetchIncentives]);

    return (
        <div className="flex flex-col space-y-8 animate-in fade-in duration-500">
            {/* Header Section */}
            <div className="flex flex-col space-y-2">
                <h1 className="text-3xl font-black text-white tracking-tight">Mission Control</h1>
                <p className="text-xs text-gray-500 font-bold uppercase tracking-[0.2em]">Daily Challenges & Rewards</p>
            </div>

            {/* Quick Stats Overview */}
            <div className="flex overflow-x-auto pb-4 gap-4 md:grid md:grid-cols-3 md:gap-6 md:overflow-visible md:pb-0 scrollbar-hide">
                <div className="glass-morphism-dark p-6 rounded-[2rem] border border-white/5 flex items-center space-x-4 min-w-[200px] flex-shrink-0">
                    <div className="w-12 h-12 rounded-2xl flex-shrink-0 bg-orange-500/10 flex items-center justify-center text-orange-500">
                        <FaFire className="text-xl" />
                    </div>
                    <div>
                        <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Active Streak</p>
                        <p className="text-lg font-black text-white">5 Days</p>
                    </div>
                </div>
                <div className="glass-morphism-dark p-6 rounded-[2rem] border border-white/5 flex items-center space-x-4 min-w-[200px] flex-shrink-0">
                    <div className="w-12 h-12 rounded-2xl flex-shrink-0 bg-emerald-500/10 flex items-center justify-center text-emerald-500">
                        <FaRupeeSign className="text-xl" />
                    </div>
                    <div>
                        <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Bonus Earned</p>
                        <p className="text-lg font-black text-white">₹450</p>
                    </div>
                </div>
                <div className="glass-morphism-dark p-6 rounded-[2rem] border border-white/5 flex items-center space-x-4 min-w-[200px] flex-shrink-0">
                    <div className="w-12 h-12 rounded-2xl flex-shrink-0 bg-blue-500/10 flex items-center justify-center text-blue-500">
                        <FaChartLine className="text-xl" />
                    </div>
                    <div>
                        <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Efficiency</p>
                        <p className="text-lg font-black text-white">98%</p>
                    </div>
                </div>
            </div>

            {/* Missions List */}
            <div className="space-y-6">
                <h3 className="text-xs font-black text-gray-400 uppercase tracking-[0.3em] ml-2">Available Missions</h3>

                {loading ? (
                    <div className="flex justify-center p-20">
                        <div className="w-8 h-8 border-2 border-t-orange-500 border-white/5 rounded-full animate-spin"></div>
                    </div>
                ) : incentives.length === 0 ? (
                    <div className="glass-morphism-dark p-12 rounded-[2.5rem] border border-white/5 text-center">
                        <FaTrophy className="text-4xl text-gray-800 mx-auto mb-4" />
                        <h4 className="text-white font-black text-xl">All Missions Completed</h4>
                        <p className="text-gray-500 text-sm mt-1">Check back tomorrow for new challenges.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
                        {incentives.map((progress, idx) => (
                            <motion.div
                                key={progress.id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.1 }}
                                className="glass-morphism-dark p-8 rounded-[2.5rem] border border-white/5 relative overflow-hidden group"
                            >
                                <div className="absolute top-0 right-0 p-6">
                                    <div className="px-3 py-1.5 rounded-xl bg-emerald-500/10 text-emerald-500 text-[10px] font-black uppercase tracking-widest border border-emerald-500/20">
                                        + ₹{progress.scheme_details.reward_amount}
                                    </div>
                                </div>

                                <div className="mb-6">
                                    <h3 className="text-xl font-black text-white tracking-tight mb-2 pr-20">{progress.scheme_details.title}</h3>
                                    <p className="text-xs text-gray-500 font-medium leading-relaxed">{progress.scheme_details.description}</p>
                                </div>

                                <div className="space-y-4">
                                    <div className="flex justify-between items-end">
                                        <div className="space-y-1">
                                            <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Progress</p>
                                            <p className="text-sm font-black text-white">
                                                {progress.current_count} <span className="text-gray-600">/</span> {progress.scheme_details.target_count} <span className="text-[10px] text-gray-500 uppercase ml-1">Orders</span>
                                            </p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-[18px] font-black text-orange-500">{Math.round((progress.current_count / progress.scheme_details.target_count) * 100)}%</p>
                                        </div>
                                    </div>

                                    <div className="h-2.5 w-full bg-white/5 rounded-full overflow-hidden border border-white/5">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${(progress.current_count / progress.scheme_details.target_count) * 100}%` }}
                                            className="h-full bg-gradient-to-r from-orange-600 to-orange-400 shadow-[0_0_15px_rgba(255,48,8,0.3)]"
                                        />
                                    </div>
                                </div>

                                <div className="mt-8 flex items-center justify-between">
                                    <div className="flex items-center space-x-2 text-gray-500">
                                        <FaClock className="text-[10px]" />
                                        <span className="text-[9px] font-black uppercase tracking-widest">Ends in 4h 20m</span>
                                    </div>
                                    {progress.is_completed ? (
                                        <div className="flex items-center space-x-2 text-emerald-500">
                                            <FaCheckCircle className="text-sm" />
                                            <span className="text-[9px] font-black uppercase tracking-widest">Claimed</span>
                                        </div>
                                    ) : (
                                        <button className="px-4 py-2 rounded-lg bg-white/5 text-white text-[9px] font-black uppercase tracking-widest border border-white/5 hover:bg-white/10 transition-all">
                                            Details
                                        </button>
                                    )}
                                </div>
                            </motion.div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default RiderMissions;
