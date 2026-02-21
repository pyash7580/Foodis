import { API_BASE_URL } from '../../../config';

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '../../../contexts/AuthContext';
import toast from 'react-hot-toast';

const ProfileHome = () => {
    const { user, token, updateUser } = useAuth(); // Assuming updateUser exists in AuthContext to refresh local user data
    const [stats, setStats] = useState({ total_orders: 0, total_spent: 0, member_since: null });
    const [loading, setLoading] = useState(true);
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({ name: '', email: '' });

    const fetchProfileData = useCallback(async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/api/auth/profile/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
            });
            setStats({
                total_orders: res.data.total_orders,
                total_spent: res.data.total_spent,
                member_since: res.data.created_at
            });
            setFormData({
                name: res.data.name,
                email: res.data.email
            });
            setLoading(false);
        } catch (error) {
            console.error("Profile fetch error", error);
            setLoading(false);
        }
    }, [token]);

    useEffect(() => {
        if (token) {
            fetchProfileData();
        }
    }, [token, fetchProfileData]);

    const handleUpdateProfile = async (e) => {
        e.preventDefault();
        try {
            const res = await axios.patch(`${API_BASE_URL}/api/auth/profile/update/`, formData, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
            });
            toast.success("Profile updated successfully!");
            setIsEditing(false);
            if (updateUser) updateUser(res.data); // Update context if function exists
        } catch (error) {
            toast.error("Failed to update profile");
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-400 font-bold">Loading Profile...</div>;

    return (
        <div className="space-y-6">
            <div className="bg-gradient-to-r from-red-600 to-red-500 rounded-3xl p-8 text-white shadow-xl relative overflow-hidden">
                <div className="relative z-10 flex items-center space-x-6">
                    <div className="h-24 w-24 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center text-4xl font-bold border-2 border-white/30 shadow-inner">
                        {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
                    </div>
                    <div>
                        <h1 className="text-3xl font-black tracking-tight">{user.name}</h1>
                        <p className="text-red-100 font-medium flex items-center mt-1">
                            {user.phone}
                            <span className="ml-2 px-2 py-0.5 bg-white/20 rounded-full text-[10px] font-bold uppercase tracking-widest backdrop-blur-sm border border-white/10">
                                {user.is_verified ? 'Verified' : 'Unverified'}
                            </span>
                        </p>
                        <p className="text-red-100 text-sm mt-1">{user.email}</p>
                    </div>
                    <button
                        onClick={() => setIsEditing(!isEditing)}
                        className="absolute top-8 right-8 bg-white/10 hover:bg-white/20 p-2 rounded-xl transition backdrop-blur-sm border border-white/10"
                    >
                        ✏️ Edit
                    </button>
                </div>

                {/* Decorative circles */}
                <div className="absolute top-0 right-0 -mt-16 -mr-16 w-64 h-64 rounded-full bg-white/10 blur-3xl"></div>
                <div className="absolute bottom-0 left-0 -mb-16 -ml-16 w-64 h-64 rounded-full bg-black/5 blur-3xl"></div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <p className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-1">Total Orders</p>
                    <p className="text-3xl font-black text-gray-900">{stats.total_orders}</p>
                </div>
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <p className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-1">Total Spent</p>
                    <p className="text-3xl font-black text-gray-900">₹{stats.total_spent.toLocaleString()}</p>
                </div>
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <p className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-1">Member Since</p>
                    <p className="text-xl font-black text-gray-900">
                        {stats.member_since ? new Date(stats.member_since).toLocaleDateString([], { month: 'long', year: 'numeric' }) : 'N/A'}
                    </p>
                </div>
            </div>

            {/* Edit Form */}
            {isEditing && (
                <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 animate-in fade-in slide-in-from-top-4 duration-300">
                    <h2 className="text-xl font-black text-gray-900 mb-6">Edit Profile</h2>
                    <form onSubmit={handleUpdateProfile} className="space-y-6 max-w-lg">
                        <div>
                            <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Full Name</label>
                            <input
                                type="text"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                className="w-full bg-gray-50 border border-gray-100 rounded-2xl p-4 font-bold text-gray-900 focus:ring-4 focus:ring-red-100 focus:border-red-500 transition outline-none"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Email Address</label>
                            <input
                                type="email"
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                className="w-full bg-gray-50 border border-gray-100 rounded-2xl p-4 font-bold text-gray-900 focus:ring-4 focus:ring-red-100 focus:border-red-500 transition outline-none"
                            />
                        </div>
                        <div className="flex space-x-4">
                            <button type="button" onClick={() => setIsEditing(false)} className="px-6 py-3 rounded-xl font-bold text-gray-500 hover:bg-gray-100 transition">
                                Cancel
                            </button>
                            <button type="submit" className="px-8 py-3 bg-red-600 text-white rounded-xl font-bold shadow-lg shadow-red-100 hover:bg-red-700 transition transform hover:scale-[1.02]">
                                Save Changes
                            </button>
                        </div>
                    </form>
                </div>
            )}
        </div>
    );
};

export default ProfileHome;
