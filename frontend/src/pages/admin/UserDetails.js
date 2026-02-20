
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../config';
import toast from 'react-hot-toast';
import { FaTimes, FaUser, FaMapMarkerAlt, FaWallet, FaHistory, FaPhone, FaEnvelope, FaCalendarAlt } from 'react-icons/fa';
import { format } from 'date-fns';

const UserDetails = ({ userId, onClose }) => {
    const [details, setDetails] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDetails = async () => {
            try {
                const token = localStorage.getItem('token_admin');
                const res = await axios.get(`${API_BASE_URL}/api/admin/users/${userId}/details/`, {
                    headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' }
                });
                setDetails(res.data);
            } catch (error) {
                console.error("Failed to load user details", error);
                toast.error("Failed to load details");
                onClose();
            } finally {
                setLoading(false);
            }
        };
        fetchDetails();
    }, [userId]);

    if (loading) return (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
            <div className="bg-white p-6 rounded-xl animate-pulse">Loading Details...</div>
        </div>
    );

    if (!details) return null;

    const { profile, addresses, wallet_balance, recent_orders } = details;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl relative">
                {/* Header */}
                <div className="sticky top-0 bg-white border-b border-gray-100 p-6 flex justify-between items-center z-10">
                    <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center text-xl font-bold text-gray-500">
                            {profile.name?.charAt(0) || 'U'}
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-gray-800">{profile.name}</h2>
                            <span className={`text-xs px-2 py-1 rounded-full font-bold ${profile.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                {profile.is_active ? 'Active Customer' : 'Blocked Account'}
                            </span>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full transition">
                        <FaTimes className="text-xl text-gray-500" />
                    </button>
                </div>

                <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left Column: Personal Info & Wallet */}
                    <div className="space-y-6">
                        <div className="bg-gray-50 p-6 rounded-xl border border-gray-100">
                            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wide mb-4 flex items-center gap-2">
                                <FaUser /> Personal Details
                            </h3>
                            <div className="space-y-3">
                                <div className="flex items-center text-gray-700">
                                    <FaPhone className="w-5 text-gray-400 mr-3" />
                                    <span>{profile.phone}</span>
                                </div>
                                <div className="flex items-center text-gray-700">
                                    <FaEnvelope className="w-5 text-gray-400 mr-3" />
                                    <span>{profile.email || 'No Email'}</span>
                                </div>
                                <div className="flex items-center text-gray-700">
                                    <FaCalendarAlt className="w-5 text-gray-400 mr-3" />
                                    <span>Joined: {format(new Date(profile.created_at), 'MMM dd, yyyy')}</span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-green-50 p-6 rounded-xl border border-green-100">
                            <h3 className="text-sm font-bold text-green-600 uppercase tracking-wide mb-2 flex items-center gap-2">
                                <FaWallet /> Foodis Wallet
                            </h3>
                            <p className="text-3xl font-black text-green-700">₹{parseFloat(wallet_balance).toLocaleString()}</p>
                            <p className="text-xs text-green-600 mt-1">Available balance</p>

                            {details.wallet_transactions && details.wallet_transactions.length > 0 && (
                                <div className="mt-4 pt-4 border-t border-green-200">
                                    <p className="text-xs font-bold text-green-800 mb-2 uppercase">Recent Transactions</p>
                                    <div className="space-y-2">
                                        {details.wallet_transactions.map(tx => (
                                            <div key={tx.id} className="flex justify-between text-xs text-green-900">
                                                <span>{tx.description}</span>
                                                <span className={tx.transaction_type === 'CREDIT' ? 'text-green-700 font-bold' : 'text-red-600 font-bold'}>
                                                    {tx.transaction_type === 'CREDIT' ? '+' : '-'}₹{parseFloat(tx.amount)}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Middle & Right: Addresses & Orders */}
                    <div className="col-span-1 lg:col-span-2 space-y-6">
                        {/* Addresses */}
                        <div className="bg-white border border-gray-100 rounded-xl p-6">
                            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wide mb-4 flex items-center gap-2">
                                <FaMapMarkerAlt /> Saved Addresses
                            </h3>
                            <div className="grid gap-3">
                                {addresses.length > 0 ? addresses.map(addr => (
                                    <div key={addr.id} className="p-3 bg-gray-50 rounded-lg text-sm text-gray-600">
                                        <div className="flex items-center gap-2 font-bold text-gray-800 mb-1">
                                            <span className="uppercase text-xs bg-gray-200 px-2 py-0.5 rounded text-gray-600">{addr.label}</span>
                                            {addr.default && <span className="text-xs text-green-600">(Default)</span>}
                                        </div>
                                        <p>{addr.address_line1}, {addr.address_line2}</p>
                                        <p>{addr.city}, {addr.state} - {addr.pincode}</p>
                                    </div>
                                )) : <p className="text-gray-400 text-sm">No addresses saved.</p>}
                            </div>
                        </div>

                        {/* Recent Orders */}
                        <div>
                            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wide mb-4 flex items-center gap-2">
                                <FaHistory /> Recent Orders
                            </h3>
                            <div className="space-y-3">
                                {recent_orders.length > 0 ? recent_orders.map(order => (
                                    <div key={order.id} className="flex justify-between items-center p-4 bg-white border border-gray-100 rounded-xl hover:shadow-sm transition">
                                        <div>
                                            <div className="flex items-center gap-2">
                                                <span className="font-bold text-gray-800">#{order.order_id}</span>
                                                <span className={`text-xs px-2 py-0.5 rounded font-bold ${order.status === 'DELIVERED' ? 'bg-green-100 text-green-700' :
                                                    order.status === 'CANCELLED' ? 'bg-red-100 text-red-700' :
                                                        'bg-blue-100 text-blue-700'
                                                    }`}>{order.status}</span>
                                            </div>
                                            <p className="text-xs text-gray-500 mt-1">
                                                {format(new Date(order.placed_at), 'MMM dd, hh:mm a')} • {order.restaurant_name}
                                            </p>
                                        </div>
                                        <div className="text-right">
                                            <p className="font-bold text-gray-800">₹{parseFloat(order.total).toLocaleString()}</p>
                                            <p className="text-xs text-gray-400 uppercase">{order.payment_method}</p>
                                        </div>
                                    </div>
                                )) : <p className="text-gray-400 text-sm">No recent orders.</p>}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UserDetails;
