import { API_BASE_URL } from '../../config';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import ProfileLayout from '../../components/ProfileLayout';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const Profile = () => {
    const { user, token } = useAuth();
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/api/client/profile/me/`, {
                    headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
                });
                setStats(response.data);
            } catch (error) {
                console.error('Error fetching profile stats:', error);
            } finally {
                setLoading(false);
            }
        };

        if (user && token) fetchStats();
    }, [user, token]);

    if (!user) return null;

    if (loading) {
        return (
            <ProfileLayout>
                <div className="animate-pulse flex flex-col items-center justify-center h-64">
                    <div className="h-20 w-20 bg-gray-200 rounded-full mb-4"></div>
                    <div className="h-4 w-48 bg-gray-200 rounded"></div>
                </div>
            </ProfileLayout>
        );
    }

    return (
        <ProfileLayout>
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-8"
            >
                {/* Header Section */}
                <div className="bg-white rounded-3xl p-8 shadow-sm border border-gray-100 flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-8">
                    <div className="relative group">
                        <div className="h-32 w-32 rounded-full border-4 border-white shadow-lg bg-red-600 flex items-center justify-center text-white text-5xl font-bold">
                            {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
                        </div>
                        <button className="absolute bottom-0 right-0 bg-white p-2 rounded-full shadow-md border hover:bg-gray-50 transition-colors">
                            📷
                        </button>
                    </div>
                    <div className="flex-1 text-center md:text-left pt-2">
                        <div className="flex flex-col md:flex-row md:items-center md:space-x-4 mb-2">
                            <h1 className="text-3xl font-extrabold text-gray-900">{user.name}</h1>
                            {user.is_verified && (
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 self-center">
                                    Verified ✓
                                </span>
                            )}
                        </div>
                        <div className="space-y-1 text-gray-500 mb-6 font-medium">
                            <p className="flex items-center justify-center md:justify-start">
                                <span className="mr-2 text-lg">📱</span> {user.phone}
                            </p>
                            <p className="flex items-center justify-center md:justify-start">
                                <span className="mr-2 text-lg">✉️</span> {user.email || 'Email not set'}
                            </p>
                        </div>
                        <Link
                            to="/client/profile/edit"
                            className="inline-flex items-center px-6 py-2.5 border border-red-600 text-red-600 font-bold rounded-lg hover:bg-red-50 transition-all duration-200"
                        >
                            Edit Profile
                        </Link>
                    </div>
                </div>

                {/* Quick Stats Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 text-center hover:shadow-md transition-shadow cursor-default">
                        <div className="text-3xl mb-2">📦</div>
                        <div className="text-2xl font-black text-gray-900">{stats?.total_orders || 0}</div>
                        <div className="text-sm font-bold text-gray-400 uppercase tracking-tighter">Total Orders</div>
                    </div>
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 text-center hover:shadow-md transition-shadow cursor-default">
                        <div className="text-3xl mb-2">💰</div>
                        <div className="text-2xl font-black text-gray-900">₹{stats?.total_spend || 0}</div>
                        <div className="text-sm font-bold text-gray-400 uppercase tracking-tighter">Spent on Food</div>
                    </div>
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 text-center hover:shadow-md transition-shadow cursor-default">
                        <div className="text-3xl mb-2">📅</div>
                        <div className="text-2xl font-black text-gray-900">
                            {new Date(user.created_at).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' })}
                        </div>
                        <div className="text-sm font-bold text-gray-400 uppercase tracking-tighter">Member Since</div>
                    </div>
                </div>

                {/* Account Settings / Actions */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                        <h3 className="text-xl font-black text-gray-900 mb-6 flex items-center">
                            <span className="mr-3">⚙️</span> Account Settings
                        </h3>
                        <div className="space-y-2">
                            <div className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors">
                                <div className="flex items-center">
                                    <span className="text-xl mr-4">🌐</span>
                                    <div>
                                        <p className="font-bold text-gray-800">Language Preference</p>
                                        <p className="text-xs text-gray-500">{user.language_preference || 'English'}</p>
                                    </div>
                                </div>
                                <button className="text-sm font-bold text-red-600 hover:underline">Change</button>
                            </div>
                            <div className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors">
                                <div className="flex items-center">
                                    <span className="text-xl mr-4">🔏</span>
                                    <p className="font-bold text-gray-800">Change Password</p>
                                </div>
                                <button className="text-sm font-bold text-red-600 hover:underline">Settings</button>
                            </div>
                        </div>
                    </div>

                    <div className="bg-red-600 rounded-2xl p-8 shadow-xl text-white flex flex-col justify-between overflow-hidden relative group">
                        <div className="absolute -right-12 -top-12 h-32 w-32 bg-white/10 rounded-full blur-2xl group-hover:bg-white/20 transition-all duration-700"></div>
                        <div className="relative z-10">
                            <h3 className="text-2xl font-black mb-2">Stay Safe & Secure</h3>
                            <p className="text-red-100 text-sm opacity-80 leading-relaxed mb-6">
                                We never share your data with 3rd parties. Your payment methods are PCI-DSS compliant and encrypted.
                            </p>
                            <button className="bg-white text-red-600 px-6 py-2.5 rounded-lg font-black text-sm shadow-lg hover:bg-red-50 transition-all">
                                Security Checkup
                            </button>
                        </div>
                    </div>
                </div>
            </motion.div>
        </ProfileLayout>
    );
};

export default Profile;
