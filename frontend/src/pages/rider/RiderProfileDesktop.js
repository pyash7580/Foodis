import React, { useState, useEffect } from 'react';
import { FaUser, FaPhone, FaMapMarkerAlt, FaMotorcycle, FaStar, FaIdCard } from 'react-icons/fa';
import { motion } from 'framer-motion';
import { useRider } from '../../contexts/RiderContext';

const RiderProfileDesktop = () => {
    const { profile } = useRider();
    const [loading, setLoading] = useState(!profile);

    useEffect(() => {
        if (profile) setLoading(false);
    }, [profile]);

    if (loading) return (
        <div className="flex items-center justify-center h-full">
            <p className="text-2xl font-bold text-gray-400">Loading Profile...</p>
        </div>
    );

    return (
        <div className="h-full p-8 space-y-8 overflow-auto relative">
            {/* Background Decorative Blobs */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-blue-600/10 rounded-full blur-[100px] -mr-32 -mt-32"></div>

            {/* Profile Header Card */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card p-10 rounded-[2.5rem] relative overflow-hidden group border border-white/10"
            >
                <div className="flex flex-col md:flex-row items-center md:space-x-8 relative z-10 text-center md:text-left">
                    <div className="w-32 h-32 rounded-[2rem] bg-gradient-to-br from-[#FF3008] to-[#FF6B00] flex items-center justify-center shadow-2xl relative mb-6 md:mb-0">
                        <FaUser className="text-white text-5xl" />
                        <div className="absolute -bottom-2 -right-2 w-10 h-10 bg-[#0F172A] rounded-xl border border-white/10 flex items-center justify-center">
                            <FaStar className="text-yellow-400 text-lg" />
                        </div>
                    </div>
                    <div className="flex-1 w-full">
                        <div className="flex flex-col md:flex-row md:items-center justify-between mb-4 space-y-4 md:space-y-0">
                            <div>
                                <h1 className="text-4xl md:text-5xl font-black text-white tracking-tighter mb-2">{profile?.rider_name || 'Rider Partner'}</h1>
                                <div className="flex flex-wrap items-center justify-center md:justify-start gap-4">
                                    <span className={`px-5 py-1.5 rounded-full font-black text-[10px] uppercase tracking-widest border ${profile?.status === 'APPROVED' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/20' : 'bg-orange-500/20 text-orange-400 border-orange-500/20'}`}>
                                        Account {profile?.status}
                                    </span>
                                    <div className="flex items-center space-x-2 bg-white/5 px-4 py-1.5 rounded-full border border-white/5">
                                        <FaStar className="text-yellow-400 text-xs" />
                                        <span className="font-black text-white text-sm">{profile?.rating?.toFixed(1) || '4.9'}</span>
                                    </div>
                                </div>
                            </div>
                            <div className="text-center md:text-right pt-4 md:pt-0 border-t border-white/10 md:border-t-0 mt-4 md:mt-0">
                                <p className="text-[10px] text-gray-500 font-black uppercase tracking-[0.3em] mb-1">Partner ID</p>
                                <p className="font-black text-white text-lg tracking-widest">#{profile?.id?.toString().padStart(6, '0')}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 pb-10">
                <div className="lg:col-span-2 space-y-8">
                    {/* Information Grid */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="glass-morphism-dark p-8 rounded-[2.5rem] border border-white/10 shadow-2xl"
                    >
                        <h3 className="text-xl font-black text-white tracking-tight mb-8 flex items-center">
                            <span className="w-8 h-1 bg-blue-500 rounded-full mr-3"></span>
                            Identity & Operations
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="p-6 bg-white/5 rounded-3xl border border-white/5 hover:bg-white/10 transition-colors">
                                <div className="flex items-center space-x-4 mb-4">
                                    <div className="p-3 bg-blue-500/20 rounded-2xl">
                                        <FaPhone className="text-blue-400" />
                                    </div>
                                    <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest">Mobile Number</p>
                                </div>
                                <p className="text-xl font-black text-white">{profile?.mobile_number || 'N/A'}</p>
                            </div>

                            <div className="p-6 bg-white/5 rounded-3xl border border-white/5 hover:bg-white/10 transition-colors">
                                <div className="flex items-center space-x-4 mb-4">
                                    <div className="p-3 bg-emerald-500/20 rounded-2xl">
                                        <FaMapMarkerAlt className="text-emerald-400" />
                                    </div>
                                    <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest">Operating City</p>
                                </div>
                                <p className="text-xl font-black text-white">{profile?.city || 'N/A'}</p>
                            </div>

                            <div className="p-6 bg-white/5 rounded-3xl border border-white/5 hover:bg-white/10 transition-colors">
                                <div className="flex items-center space-x-4 mb-4">
                                    <div className="p-3 bg-purple-500/20 rounded-2xl">
                                        <FaMotorcycle className="text-purple-400" />
                                    </div>
                                    <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest">Vehicle Number</p>
                                </div>
                                <p className="text-xl font-black text-white">{profile?.vehicle_number || 'N/A'}</p>
                            </div>

                            <div className="p-6 bg-white/5 rounded-3xl border border-white/5 hover:bg-white/10 transition-colors">
                                <div className="flex items-center space-x-4 mb-4">
                                    <div className="p-3 bg-orange-500/20 rounded-2xl">
                                        <FaIdCard className="text-orange-400" />
                                    </div>
                                    <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest">License Detail</p>
                                </div>
                                <p className="text-xl font-black text-white truncate">{profile?.license_number || 'N/A'}</p>
                            </div>
                        </div>
                    </motion.div>

                    {/* Bank Details */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="glass-morphism-dark p-8 rounded-[2.5rem] border border-white/10 shadow-2xl"
                    >
                        <h3 className="text-xl font-black text-white tracking-tight mb-8 flex items-center">
                            <span className="w-8 h-1 bg-emerald-500 rounded-full mr-3"></span>
                            Financial Settlement Details
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="space-y-4">
                                <div className="flex justify-between items-center bg-white/5 p-4 rounded-2xl border border-white/5">
                                    <span className="text-[10px] font-black text-gray-500 uppercase">Bank Name</span>
                                    <span className="font-bold text-white">{profile?.bank_details?.bank_name || 'N/A'}</span>
                                </div>
                                <div className="flex justify-between items-center bg-white/5 p-4 rounded-2xl border border-white/5">
                                    <span className="text-[10px] font-black text-gray-500 uppercase">Account No</span>
                                    <span className="font-bold text-white">{profile?.bank_details?.account_number || '•••• 8890'}</span>
                                </div>
                            </div>
                            <div className="space-y-4">
                                <div className="flex justify-between items-center bg-white/5 p-4 rounded-2xl border border-white/5">
                                    <span className="text-[10px] font-black text-gray-500 uppercase">IFSC Code</span>
                                    <span className="font-bold text-white">{profile?.bank_details?.ifsc_code || 'N/A'}</span>
                                </div>
                                <div className="flex justify-between items-center bg-white/5 p-4 rounded-2xl border border-white/5">
                                    <span className="text-[10px] font-black text-gray-500 uppercase">Holder</span>
                                    <span className="font-bold text-white truncate max-w-[150px]">{profile?.bank_details?.account_holder_name || profile?.rider_name}</span>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </div>

                <div className="space-y-8">
                    {/* Performance Sidebar */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="glass-morphism-dark p-8 rounded-[2.5rem] border border-white/10 h-full flex flex-col"
                    >
                        <h3 className="text-xl font-black text-white tracking-tight mb-10 text-center">Lifetime Impact</h3>

                        <div className="space-y-8 flex-1">
                            <div className="text-center">
                                <div className="text-5xl font-black text-white mb-2 tracking-tighter">{profile?.total_deliveries || 0}</div>
                                <p className="text-[10px] text-gray-500 font-black uppercase tracking-[0.3em]">Total Deliveries</p>
                            </div>

                            <div className="h-px bg-white/5"></div>

                            <div className="text-center">
                                <div className="text-5xl font-black text-emerald-400 mb-2 tracking-tighter">₹{profile?.wallet_balance || 0}</div>
                                <p className="text-[10px] text-gray-500 font-black uppercase tracking-[0.3em]">Total Earnings</p>
                            </div>

                            <div className="h-px bg-white/5"></div>

                            <div className="flex flex-col items-center">
                                <div className="text-center mb-6">
                                    <p className="text-[10px] text-gray-500 font-black uppercase tracking-[0.3em] mb-4">KYC Documents</p>
                                    <div className="grid grid-cols-2 gap-3">
                                        <div className="p-3 bg-white/5 rounded-2xl border border-white/5 text-[9px] font-black text-gray-400">AADHAR: VERIFIED</div>
                                        <div className="p-3 bg-white/5 rounded-2xl border border-white/5 text-[9px] font-black text-gray-400">PAN: VERIFIED</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <button className="w-full bg-white/5 hover:bg-white/10 py-5 rounded-2xl font-black text-[10px] uppercase tracking-widest text-gray-400 border border-white/5 mt-10 transition-all">
                            Update Documentation
                        </button>
                    </motion.div>
                </div>
            </div>
        </div>
    );
};

export default RiderProfileDesktop;
