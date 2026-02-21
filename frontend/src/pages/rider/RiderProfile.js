import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../config';
import { FaUser, FaMotorcycle, FaMapMarkerAlt, FaSignOutAlt, FaIdCard, FaWallet, FaStar } from 'react-icons/fa';

import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';

const RiderProfile = () => {
    const { logout } = useAuth();
    const navigate = useNavigate();
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);

    const token = localStorage.getItem('token_rider');

    useEffect(() => {
        if (!token) {
            navigate('/rider/login');
            return;
        }
        // Use dashboard API for comprehensive data
        const timestamp = new Date().getTime();
        axios.get(`${API_BASE_URL}/api/rider/profile/dashboard/?_t=${timestamp}`, { headers: { Authorization: `Bearer ${token}`, 'X-Role': 'RIDER' } })
            .then(res => {
                if (res.data && res.data.profile) {
                    setProfile(res.data.profile);
                }
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, [token, navigate]);


    const handleLogout = () => {
        logout();
        navigate('/rider/login');
    };

    if (loading) return <div className="p-10 text-center text-gray-400 font-bold">Loading Profile...</div>;
    if (!profile) return <div className="p-10 text-center">Profile not found.</div>;

    return (
        <div className="min-h-screen bg-[#0F172A] pb-24 font-jakarta text-white relative overflow-hidden">
            {/* Background Decorative Blobs */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
                <div className="absolute top-[-10%] right-[-10%] w-[60%] h-[40%] bg-blue-600/10 rounded-full blur-[100px]"></div>
                <div className="absolute bottom-[-10%] left-[-10%] w-[60%] h-[40%] bg-red-600/10 rounded-full blur-[100px]"></div>
            </div>

            <div className="glass-morphism-dark p-6 shadow-2xl sticky top-0 z-[100] border-b border-white/5 flex justify-between items-center">
                <h1 className="font-black text-sm text-gray-400 uppercase tracking-[0.2em] ml-2">Partner Profile</h1>
                <div className="w-8"></div>
            </div>

            <div className="p-6 space-y-6 relative z-10">
                {/* Avatar & Name Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="glass-card p-10 rounded-[3rem] text-center border border-white/10 relative overflow-hidden"
                >
                    <div className="absolute top-0 right-0 w-32 h-32 bg-[#FF3008]/10 rounded-full blur-3xl -mr-16 -mt-16"></div>

                    <div className="w-28 h-28 bg-gradient-to-br from-[#FF3008] to-[#FF6B00] rounded-[2.5rem] mx-auto mb-6 flex items-center justify-center shadow-2xl relative">
                        <FaUser className="text-white text-4xl" />
                        <div className="absolute -bottom-2 -right-2 w-10 h-10 bg-[#0F172A] rounded-xl border border-white/10 flex items-center justify-center">
                            <FaStar className="text-yellow-400 text-sm" />
                        </div>
                    </div>

                    <h2 className="text-3xl font-black text-white tracking-tighter mb-1">{profile.rider_name || 'Rider Name'}</h2>
                    <p className="text-gray-500 font-bold uppercase text-[10px] tracking-widest mb-6">{profile.mobile_number}</p>

                    <span className={`px-6 py-2 rounded-full text-[10px] font-black uppercase tracking-[0.2em] border ${profile.status === 'APPROVED' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/20' : 'bg-orange-500/20 text-orange-400 border-orange-500/20'}`}>
                        {profile.status}
                    </span>
                </motion.div>

                {/* Lifetime Stats */}
                <div className="grid grid-cols-2 gap-4">
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 }}
                        className="glass-card p-6 rounded-[2.2rem] border border-white/5 text-center"
                    >
                        <div className="p-3 bg-emerald-500/20 w-fit rounded-2xl mx-auto mb-4">
                            <FaWallet className="text-emerald-400" />
                        </div>
                        <p className="text-2xl font-black text-white tracking-tighter">₹{profile.wallet_balance}</p>
                        <p className="text-[8px] text-gray-500 font-black uppercase tracking-[0.2em] mt-1">Earnings</p>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 }}
                        className="glass-card p-6 rounded-[2.2rem] border border-white/5 text-center"
                    >
                        <div className="p-3 bg-blue-500/20 w-fit rounded-2xl mx-auto mb-4">
                            <FaMotorcycle className="text-blue-400" />
                        </div>
                        <p className="text-2xl font-black text-white tracking-tighter">{profile.total_deliveries}</p>
                        <p className="text-[8px] text-gray-500 font-black uppercase tracking-[0.2em] mt-1">Deliveries</p>
                    </motion.div>
                </div>

                {/* Information Sections */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="glass-card p-8 rounded-[2.5rem] border border-white/10 space-y-8"
                >
                    <div className="flex items-center group">
                        <div className="w-12 h-12 bg-white/5 rounded-2xl border border-white/5 flex items-center justify-center mr-5 group-hover:bg-blue-500/20 transition-all">
                            <FaMapMarkerAlt className="text-blue-400" />
                        </div>
                        <div className="flex-1">
                            <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest mb-1">Operating City</p>
                            <p className="font-black text-white text-sm">{profile.city}</p>
                        </div>
                    </div>

                    <div className="flex items-center group">
                        <div className="w-12 h-12 bg-white/5 rounded-2xl border border-white/5 flex items-center justify-center mr-5 group-hover:bg-purple-500/20 transition-all">
                            <FaMotorcycle className="text-purple-400" />
                        </div>
                        <div className="flex-1">
                            <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest mb-1">Vehicle Details</p>
                            <p className="font-black text-white text-sm uppercase">{profile.vehicle_number}</p>
                            <p className="text-[8px] text-gray-500 font-bold uppercase mt-0.5">{profile.vehicle_type}</p>
                        </div>
                    </div>

                    <div className="flex items-center group">
                        <div className="w-12 h-12 bg-white/5 rounded-2xl border border-white/5 flex items-center justify-center mr-5 group-hover:bg-orange-500/20 transition-all">
                            <FaIdCard className="text-orange-400" />
                        </div>
                        <div className="flex-1">
                            <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest mb-1">License Verified</p>
                            <p className="font-black text-white text-sm">{profile.license_number}</p>
                        </div>
                    </div>
                </motion.div>

                {/* Settlement Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="glass-card p-8 rounded-[2.5rem] border border-white/5"
                >
                    <h3 className="text-[10px] font-black text-gray-500 mb-6 uppercase tracking-[0.3em] text-center">Settlement Details</h3>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center py-4 border-b border-white/5">
                            <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest">Bank</p>
                            <p className="font-black text-white text-xs">{profile.bank_details?.bank_name || 'N/A'}</p>
                        </div>
                        <div className="flex justify-between items-center py-4 border-b border-white/5">
                            <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest">Account</p>
                            <p className="font-black text-white text-xs">•••• {profile.bank_details?.account_number?.slice(-4) || '8890'}</p>
                        </div>
                        <div className="flex justify-between items-center py-4">
                            <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest">IFSC</p>
                            <p className="font-black text-white text-xs">{profile.bank_details?.ifsc_code || 'N/A'}</p>
                        </div>
                    </div>
                </motion.div>

                {/* Final Actions */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.4 }}
                    className="pt-6 pb-12"
                >
                    <button
                        onClick={handleLogout}
                        className="w-full bg-[#FF3008]/10 text-[#FF3008] border border-[#FF3008]/20 py-5 rounded-[2rem] font-black text-[10px] uppercase tracking-[0.3em] active:scale-95 transition-all mb-10 flex items-center justify-center group hover:bg-[#FF3008] hover:text-white"
                    >
                        <FaSignOutAlt className="mr-3 text-lg" /> Terminate Session
                    </button>

                    <div className="text-center opacity-20">
                        <p className="text-[8px] font-black uppercase tracking-[0.5em] text-white">Foodis Partner v2.0.4 • Build Indigo</p>
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

export default RiderProfile;
