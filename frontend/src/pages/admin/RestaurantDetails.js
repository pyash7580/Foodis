
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../config';
import { FaTimes, FaStore, FaMapMarkerAlt, FaEnvelope, FaStar, FaKey } from 'react-icons/fa';


const RestaurantDetails = ({ restaurantId, onClose }) => {
    const [restaurant, setRestaurant] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDetails = async () => {
            try {
                const token = localStorage.getItem('token_admin');
                const res = await axios.get(`${API_BASE_URL}/api/admin/restaurants/${restaurantId}/`, {
                    headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' }
                });
                setRestaurant(res.data);
            } catch (error) {
                console.error("Failed to fetch restaurant details", error);
            } finally {
                setLoading(false);
            }
        };

        if (restaurantId) fetchDetails();
    }, [restaurantId]);

    if (!restaurantId) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl">
                <div className="p-6 border-b flex justify-between items-center sticky top-0 bg-white z-10">
                    <h2 className="text-2xl font-bold text-gray-800 flex items-center">
                        <FaStore className="mr-3 text-red-500" />
                        Restaurant Details
                    </h2>
                    <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full transition">
                        <FaTimes className="text-xl text-gray-500" />
                    </button>
                </div>

                {loading ? (
                    <div className="p-12 text-center text-gray-500">Loading details...</div>
                ) : restaurant ? (
                    <div className="p-6 space-y-8">
                        {/* Header Info */}
                        <div className="flex flex-col md:flex-row gap-6 items-start">
                            <div className="w-32 h-32 bg-gray-100 rounded-xl overflow-hidden shadow-sm flex-shrink-0">
                                {restaurant.image ? (
                                    <img src={restaurant.image} alt={restaurant.name} className="w-full h-full object-cover" />
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center text-gray-300">
                                        <FaStore className="text-4xl" />
                                    </div>
                                )}
                            </div>
                            <div className="flex-1">
                                <h1 className="text-3xl font-bold text-gray-900 mb-2">{restaurant.name}</h1>
                                <div className="flex flex-wrap gap-3 mb-4">
                                    <span className={`px-3 py-1 rounded-full text-sm font-bold ${restaurant.status === 'APPROVED' ? 'bg-green-100 text-green-700' :
                                        restaurant.status === 'PENDING' ? 'bg-yellow-100 text-yellow-700' :
                                            'bg-red-100 text-red-700'
                                        }`}>
                                        {restaurant.status}
                                    </span>
                                    <span className="flex items-center px-3 py-1 bg-yellow-50 text-yellow-700 rounded-full text-sm font-bold">
                                        <FaStar className="mr-1" /> {restaurant.rating || 'New'}
                                    </span>
                                </div>
                                <p className="text-gray-500 flex items-center">
                                    <FaMapMarkerAlt className="mr-2" />
                                    {restaurant.address}, {restaurant.city}, {restaurant.state} - {restaurant.pincode}
                                </p>
                            </div>
                        </div>

                        {/* Owner & Login Details */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="bg-gray-50 p-5 rounded-xl border border-gray-100">
                                <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                                    <FaEnvelope className="mr-2 text-blue-500" /> Contact Info
                                </h3>
                                <div className="space-y-3">
                                    <div>
                                        <label className="text-xs font-bold text-gray-400 uppercase">Owner Name</label>
                                        <p className="font-medium">{restaurant.owner_name}</p>
                                    </div>
                                    <div>
                                        <label className="text-xs font-bold text-gray-400 uppercase">Phone</label>
                                        <p className="font-medium">{restaurant.owner_phone || restaurant.phone || 'N/A'}</p>
                                    </div>
                                    <div>
                                        <label className="text-xs font-bold text-gray-400 uppercase">Email</label>
                                        <p className="font-medium">{restaurant.owner_email || restaurant.email || 'N/A'}</p>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-red-50 p-5 rounded-xl border border-red-100">
                                <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                                    <FaKey className="mr-2 text-red-500" /> Login Credentials
                                </h3>
                                <div className="space-y-3">
                                    <div>
                                        <label className="text-xs font-bold text-gray-400 uppercase">Login Email/Phone</label>
                                        <p className="font-medium font-mono">{restaurant.owner_email || restaurant.owner_phone}</p>
                                    </div>
                                    <div>
                                        <label className="text-xs font-bold text-gray-400 uppercase">Login Password</label>
                                        <div className="flex items-center">
                                            <p className="font-medium font-mono bg-white px-2 py-1 rounded border border-red-200 inline-block">
                                                {restaurant.password_plain || '******'}
                                            </p>
                                            <span className="ml-2 text-xs text-red-400">(Visible to Admin)</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* System Info */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <h3 className="text-lg font-bold text-gray-800 mb-2">Metadata</h3>
                                <div className="space-y-2 text-sm">
                                    <p><span className="text-gray-500">Slug:</span> {restaurant.slug}</p>
                                    <p><span className="text-gray-500">Created At:</span> {new Date(restaurant.created_at).toLocaleString()}</p>
                                    <p><span className="text-gray-500">Last Updated:</span> {new Date(restaurant.updated_at).toLocaleString()}</p>
                                </div>
                            </div>
                        </div>

                    </div>
                ) : (
                    <div className="p-12 text-center text-red-500">Detailed information not available.</div>
                )}

                <div className="p-6 border-t bg-gray-50 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-6 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg font-medium transition"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
};

export default RestaurantDetails;
