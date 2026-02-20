
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../config';
import { FaTimes, FaMotorcycle, FaBicycle, FaUser, FaEnvelope, FaPhone, FaStar, FaKey, FaIdCard } from 'react-icons/fa';

const RiderDetails = ({ riderId, onClose }) => {
    const [rider, setRider] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDetails = async () => {
            try {
                const token = localStorage.getItem('token_admin');
                const res = await axios.get(`${API_BASE_URL}/api/admin/riders/${riderId}/`, {
                    headers: { Authorization: `Bearer ${token}`, 'X-Role': 'RIDER', 'X-Role': 'ADMIN' }
                });
                setRider(res.data);
            } catch (error) {
                console.error("Failed to fetch rider details", error);
            } finally {
                setLoading(false);
            }
        };

        if (riderId) fetchDetails();
    }, [riderId]);

    if (!riderId) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl">
                <div className="p-6 border-b flex justify-between items-center sticky top-0 bg-white z-10">
                    <h2 className="text-2xl font-bold text-gray-800 flex items-center">
                        <FaMotorcycle className="mr-3 text-red-500" />
                        Rider Details
                    </h2>
                    <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full transition">
                        <FaTimes className="text-xl text-gray-500" />
                    </button>
                </div>

                {loading ? (
                    <div className="p-12 text-center text-gray-500">Loading details...</div>
                ) : rider ? (
                    <div className="p-6 space-y-8">
                        {/* Header Info */}
                        <div className="flex flex-col md:flex-row gap-6 items-start">
                            <div className="w-32 h-32 bg-gray-100 rounded-xl overflow-hidden shadow-sm flex-shrink-0">
                                {/* Profile photo if available, generic icon otherwise */}
                                <div className="w-full h-full flex items-center justify-center text-gray-300 bg-gray-50">
                                    <FaUser className="text-4xl" />
                                </div>
                            </div>
                            <div className="flex-1">
                                <h1 className="text-3xl font-bold text-gray-900 mb-2">{rider.rider_name}</h1>
                                <div className="flex flex-wrap gap-3 mb-4">
                                    <span className={`px-3 py-1 rounded-full text-sm font-bold ${rider.status === 'APPROVED' ? 'bg-green-100 text-green-700' :
                                        rider.status === 'PENDING' ? 'bg-yellow-100 text-yellow-700' :
                                            'bg-red-100 text-red-700'
                                        }`}>
                                        {rider.status}
                                    </span>
                                    <span className="flex items-center px-3 py-1 bg-yellow-50 text-yellow-700 rounded-full text-sm font-bold">
                                        <FaStar className="mr-1" /> {rider.rating || 'New'}
                                    </span>
                                    <span className="flex items-center px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-bold">
                                        {rider.total_deliveries} Deliveries
                                    </span>
                                </div>
                                <p className="text-gray-500 flex items-center">
                                    {rider.vehicle_type === 'BIKE' || rider.vehicle_type === 'SCOOTER' ? <FaMotorcycle className="mr-2" /> : <FaBicycle className="mr-2" />}
                                    {rider.vehicle_type} - <span className="font-mono ml-1 font-bold text-gray-700">{rider.vehicle_number}</span>
                                </p>
                            </div>
                        </div>

                        {/* Contact & Login Details */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="bg-gray-50 p-5 rounded-xl border border-gray-100">
                                <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                                    <FaEnvelope className="mr-2 text-blue-500" /> Contact Info
                                </h3>
                                <div className="space-y-3">
                                    <div className="flex justify-between items-center">
                                        <label className="text-xs font-bold text-gray-400 uppercase">Phone</label>
                                        <p className="font-medium">{rider.rider_phone || 'N/A'}</p>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <label className="text-xs font-bold text-gray-400 uppercase">Email</label>
                                        <p className="font-medium">{rider.rider_email || 'N/A'}</p>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <label className="text-xs font-bold text-gray-400 uppercase">Operating City</label>
                                        <p className="font-bold text-red-600 uppercase italic tracking-wider">{rider.city || 'N/A'}</p>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <label className="text-xs font-bold text-gray-400 uppercase">License No</label>
                                        <p className="font-medium font-mono">{rider.license_number || 'N/A'}</p>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-red-50 p-5 rounded-xl border border-red-100">
                                <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                                    <FaKey className="mr-2 text-red-500" /> Login & Wallet
                                </h3>
                                <div className="space-y-3">
                                    <div className="flex justify-between items-center border-b border-red-100 pb-2 mb-2">
                                        <label className="text-xs font-bold text-gray-400 uppercase">Wallet Balance</label>
                                        <p className="text-xl font-black text-red-600">₹{rider.wallet_balance}</p>
                                    </div>
                                    <div>
                                        <label className="text-xs font-bold text-gray-400 uppercase">Login ID (Phone)</label>
                                        <p className="font-medium font-mono">{rider.rider_phone}</p>
                                    </div>
                                    <div>
                                        <label className="text-xs font-bold text-gray-400 uppercase">Login Password</label>
                                        <div className="flex items-center">
                                            <p className="font-medium font-mono bg-white px-2 py-1 rounded border border-red-200 inline-block">
                                                {rider.password_plain || '********'}
                                            </p>
                                            <span className="ml-2 text-[10px] text-red-400">(Encrypted)</span>
                                        </div>

                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Bank Details */}
                        <div className="bg-blue-50 p-6 rounded-2xl border border-blue-100">
                            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                                <FaIdCard className="mr-2 text-blue-600" /> Bank Account Details
                            </h3>
                            {rider.bank_details ? (
                                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                                    <div>
                                        <label className="text-[10px] font-black text-gray-400 uppercase block mb-1">Bank Name</label>
                                        <p className="font-bold text-gray-800">{rider.bank_details.bank_name}</p>
                                    </div>
                                    <div>
                                        <label className="text-[10px] font-black text-gray-400 uppercase block mb-1">Account Number</label>
                                        <p className="font-bold text-gray-800 font-mono">{rider.bank_details.account_number}</p>
                                    </div>
                                    <div>
                                        <label className="text-[10px] font-black text-gray-400 uppercase block mb-1">IFSC Code</label>
                                        <p className="font-bold text-gray-800 font-mono">{rider.bank_details.ifsc_code}</p>
                                    </div>
                                    <div>
                                        <label className="text-[10px] font-black text-gray-400 uppercase block mb-1">Holder Name</label>
                                        <p className="font-bold text-gray-800">{rider.bank_details.account_holder_name}</p>
                                    </div>
                                </div>
                            ) : (
                                <p className="text-gray-500 italic">No bank details provided.</p>
                            )}
                        </div>

                        {/* Identity Docs */}
                        <div className="grid grid-cols-1 gap-6">
                            <div>
                                <h3 className="text-lg font-bold text-gray-800 mb-2 flex items-center"><FaIdCard className="mr-2 text-gray-500" /> Identity Proofs</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div className="p-4 border rounded-xl bg-gray-50">
                                        <label className="text-xs font-bold text-gray-400 uppercase block mb-1">Aadhaar Number</label>
                                        <p className="font-mono font-medium">{rider.aadhar_number || 'Not provided'}</p>
                                    </div>
                                    <div className="p-4 border rounded-xl bg-gray-50">
                                        <label className="text-xs font-bold text-gray-400 uppercase block mb-1">PAN Number</label>
                                        <p className="font-mono font-medium">{rider.pan_number || 'Not provided'}</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Metadata */}
                        <div className="text-xs text-gray-400 border-t pt-4 flex justify-between">
                            <p>Registered: {new Date(rider.created_at).toLocaleString()}</p>
                            <p className="font-bold uppercase tracking-widest text-red-400">Rider ID: {rider.id}</p>
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

export default RiderDetails;
