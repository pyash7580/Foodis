import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import toast from 'react-hot-toast';
import { API_BASE_URL } from '../../config';
import { useAuth } from '../../contexts/AuthContext';

// Reusing the same layout logic as MenuManagement for consistency
// Ideally this sidebar should be a shared component
const RestaurantProfile = () => {
    const { logout } = useAuth();
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({});

    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        try {
            // Correct Endpoint: /api/restaurant/restaurant/summary/ (singular router prefix)
            const res = await axios.get(`${API_BASE_URL}/api/restaurant/restaurant/summary/?_t=${new Date().getTime()}`);
            console.log("Profile Data:", res.data); // Debug log
            if (res.data && res.data.restaurant) {
                setProfile(res.data.restaurant);
                setFormData(res.data.restaurant); // Initialize form with verified data
            } else {
                toast.error("Restaurant profile not found.");
            }
            setLoading(false);
        } catch (error) {
            console.error("Profile fetch error", error);
            if (error.response?.status === 401 || error.response?.status === 403) {
                toast.error("Session expired. Please login again.");
                // Optional: Redirect to login
                // window.location.href = '/restaurant/login';
            } else {
                const msg = error.response?.data?.error || `Failed to load profile (${error.response?.status || 'Network Error'})`;
                toast.error(msg);
            }
            setLoading(false);
        }
    };

    const handleUpdate = async (e) => {
        e.preventDefault();
        try {
            // Filter out read-only fields or handle via specific endpoint
            // For now, let's assume a patch to the restaurant instance
            // Correct Endpoint: /api/restaurant/restaurant/{id}/profile/
            const res = await axios.put(`${API_BASE_URL}/api/restaurant/restaurant/${profile.id}/profile/`, formData);
            setProfile(res.data);
            setIsEditing(false);
            toast.success("Profile updated successfully");
        } catch (error) {
            console.error("Update error", error);
            toast.error("Failed to update profile");
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-500 font-bold">Loading Profile...</div>;

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
                    <Link to="/restaurant/earnings" className="flex items-center space-x-3 p-3 text-gray-500 hover:bg-gray-50 rounded-xl font-medium transition">
                        <span>💰</span> <span>Earnings & Reports</span>
                    </Link>
                    <Link to="/restaurant/profile" className="flex items-center space-x-3 p-3 bg-red-50 text-red-600 rounded-xl font-bold">
                        <span>🏢</span> <span>Restaurant Profile</span>
                    </Link>
                </nav>
                <div className="p-4 border-t border-gray-50">
                    <button onClick={logout} className="flex items-center space-x-3 p-3 w-full text-red-400 hover:bg-red-50 rounded-xl font-medium transition">
                        <span>🚪</span> <span>Logout</span>
                    </button>
                </div>
            </aside>

            <main className="flex-grow p-8">
                <header className="flex justify-between items-center mb-10">
                    <div>
                        <h1 className="text-3xl font-black text-gray-900">Restaurant Profile</h1>
                        <p className="text-gray-500 mt-1">Manage your restaurant details and settings.</p>
                    </div>
                    <button
                        onClick={() => setIsEditing(!isEditing)}
                        className={`px-6 py-3 rounded-2xl font-bold flex items-center space-x-2 transition ${isEditing ? 'bg-gray-200 text-gray-700' : 'bg-red-600 text-white shadow-lg shadow-red-100'}`}
                    >
                        <span>{isEditing ? '❌ Cancel' : '✏️ Edit Profile'}</span>
                    </button>
                </header>

                <div className="bg-white rounded-3xl p-8 shadow-sm border border-gray-50 max-w-4xl">
                    <form onSubmit={handleUpdate} className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div>
                                <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Restaurant Name</label>
                                <input
                                    disabled={!isEditing}
                                    value={formData.name || ''}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="w-full bg-gray-50 border border-gray-100 rounded-2xl p-4 font-bold text-gray-900 focus:ring-4 focus:ring-red-100 focus:border-red-500 transition outline-none disabled:opacity-60 disabled:cursor-not-allowed"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Cuisine Type</label>
                                <input
                                    disabled={!isEditing}
                                    value={formData.cuisine_type || ''}
                                    onChange={(e) => setFormData({ ...formData, cuisine_type: e.target.value })}
                                    className="w-full bg-gray-50 border border-gray-100 rounded-2xl p-4 font-bold text-gray-900 focus:ring-4 focus:ring-red-100 focus:border-red-500 transition outline-none disabled:opacity-60 disabled:cursor-not-allowed"
                                />
                            </div>

                            <div className="md:col-span-2">
                                <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Description</label>
                                <textarea
                                    disabled={!isEditing}
                                    rows="3"
                                    value={formData.description || ''}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    className="w-full bg-gray-50 border border-gray-100 rounded-2xl p-4 font-bold text-gray-900 focus:ring-4 focus:ring-red-100 focus:border-red-500 transition outline-none disabled:opacity-60 disabled:cursor-not-allowed"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">City</label>
                                <input
                                    disabled={!isEditing}
                                    value={formData.city || ''}
                                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                                    className="w-full bg-gray-50 border border-gray-100 rounded-2xl p-4 font-bold text-gray-900 focus:ring-4 focus:ring-red-100 focus:border-red-500 transition outline-none disabled:opacity-60 disabled:cursor-not-allowed"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Address</label>
                                <input
                                    disabled={!isEditing}
                                    value={formData.address || ''}
                                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                                    className="w-full bg-gray-50 border border-gray-100 rounded-2xl p-4 font-bold text-gray-900 focus:ring-4 focus:ring-red-100 focus:border-red-500 transition outline-none disabled:opacity-60 disabled:cursor-not-allowed"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Delivery Time (mins)</label>
                                <input
                                    type="number"
                                    disabled={!isEditing}
                                    value={formData.delivery_time || ''}
                                    onChange={(e) => setFormData({ ...formData, delivery_time: e.target.value })}
                                    className="w-full bg-gray-50 border border-gray-100 rounded-2xl p-4 font-bold text-gray-900 focus:ring-4 focus:ring-red-100 focus:border-red-500 transition outline-none disabled:opacity-60 disabled:cursor-not-allowed"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Minimum Order (₹)</label>
                                <input
                                    type="number"
                                    disabled={!isEditing}
                                    value={formData.min_order_amount || ''}
                                    onChange={(e) => setFormData({ ...formData, min_order_amount: e.target.value })}
                                    className="w-full bg-gray-50 border border-gray-100 rounded-2xl p-4 font-bold text-gray-900 focus:ring-4 focus:ring-red-100 focus:border-red-500 transition outline-none disabled:opacity-60 disabled:cursor-not-allowed"
                                />
                            </div>
                        </div>

                        {isEditing && (
                            <div className="pt-6 border-t border-gray-100 flex justify-end">
                                <button type="submit" className="bg-red-600 text-white px-8 py-4 rounded-2xl font-black text-lg shadow-xl shadow-red-100 hover:bg-red-700 transition transform hover:scale-[1.02]">
                                    Save Changes
                                </button>
                            </div>
                        )}
                    </form>
                </div>
            </main>
        </div>
    );
};

export default RestaurantProfile;
