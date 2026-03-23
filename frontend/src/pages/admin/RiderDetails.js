import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../config';
import toast from 'react-hot-toast';
import { FaTimes, FaMotorcycle, FaBicycle, FaUser, FaEnvelope, FaStar, FaKey, FaIdCard, FaMoneyBillWave, FaCheck, FaBan } from 'react-icons/fa';

const RiderDetails = ({ riderId, onClose }) => {
    const [rider, setRider] = useState(null);
    const [payouts, setPayouts] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchDetails = useCallback(async () => {
        try {
            const token = localStorage.getItem('token_admin');
            const [riderRes, payoutsRes] = await Promise.all([
                axios.get(`${API_BASE_URL}/api/admin/riders/${riderId}/`, {
                    headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' }
                }),
                axios.get(`${API_BASE_URL}/api/admin/riders/${riderId}/payouts/`, {
                    headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' }
                }).catch(() => ({ data: [] })) // Fallback if endpoint fails
            ]);
            setRider(riderRes.data);
            setPayouts(payoutsRes.data);
        } catch (error) {
            console.error("Failed to fetch rider details", error);
        } finally {
            setLoading(false);
        }
    }, [riderId]);

    useEffect(() => {
        if (riderId) fetchDetails();
    }, [fetchDetails, riderId]);

    const handlePayoutAction = async (payoutId, action) => {
        if (!window.confirm(`Are you sure you want to ${action} this payout?`)) return;
        try {
            const token = localStorage.getItem('token_admin');
            await axios.post(`${API_BASE_URL}/api/admin/riders/${riderId}/${action}_payout/`, 
                { payout_id: payoutId }, 
                { headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' } }
            );
            toast.success(`Payout ${action}ed successfully`);
            fetchDetails(); 
        } catch (error) {
            console.error(`Failed to ${action} payout`, error);
            toast.error(error.response?.data?.error || `Failed to ${action} payout`);
        }
    };

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
                                        <p className="text-xl font-black text-red-600">₹{parseFloat(rider.wallet_balance || 0).toFixed(2)}</p>
                                    </div>
                                    <div>
                                        <label className="text-xs font-bold text-gray-400 uppercase">Login ID (Phone)</label>
                                        <p className="font-medium font-mono">{rider.rider_phone || 'N/A'}</p>
                                    </div>
                                    <div>
                                        <label className="text-xs font-bold text-gray-400 uppercase">Login Password</label>
                                        <div className="flex items-center">
                                            <p className="font-medium font-mono bg-white px-2 py-1 rounded border border-red-200 inline-block">
                                                ••••••••••
                                            </p>
                                            <span className="ml-2 text-[10px] text-red-400">(Encrypted)</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Payout Requests */}
                        {payouts && payouts.length > 0 && (
                            <div className="bg-emerald-50 p-6 rounded-2xl border border-emerald-100">
                                <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                                    <FaMoneyBillWave className="mr-2 text-emerald-600" /> Payout Requests
                                </h3>
                                <div className="space-y-4">
                                    {payouts.map(payout => (
                                        <div key={payout.id} className="bg-white p-4 rounded-xl border border-emerald-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
                                            <div>
                                                <div className="flex items-center gap-3 mb-1">
                                                    <span className="font-black text-lg text-emerald-600">₹{payout.amount}</span>
                                                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                                                        payout.status === 'PENDING' ? 'bg-yellow-100 text-yellow-700' :
                                                        payout.status === 'PAID' ? 'bg-green-100 text-green-700' :
                                                        'bg-red-100 text-red-700'
                                                    }`}>
                                                        {payout.status}
                                                    </span>
                                                </div>
                                                <div className="text-sm text-gray-600">
                                                    <span className="font-bold">{payout.payout_method}</span>: {' '}
                                                    {payout.payout_method === 'UPI' && payout.payout_details?.upi_id}
                                                    {payout.payout_method === 'BANK' && `${payout.payout_details?.bank_name} - ${payout.payout_details?.account_number}`}
                                                    {payout.payout_method === 'CARD' && `Card: **** **** **** ${payout.payout_details?.card_number?.slice(-4) || 'N/A'}`}
                                                </div>
                                                <div className="text-xs text-gray-400 mt-1">
                                                    Requested: {new Date(payout.requested_at).toLocaleString()}
                                                    {payout.paid_at && ` • Paid: ${new Date(payout.paid_at).toLocaleString()}`}
                                                </div>
                                            </div>
                                            
                                            {payout.status === 'PENDING' && (
                                                <div className="flex gap-2">
                                                    <button 
                                                        onClick={() => handlePayoutAction(payout.id, 'accept')}
                                                        className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg font-bold flex items-center text-sm transition"
                                                    >
                                                        <FaCheck className="mr-1" /> Accept
                                                    </button>
                                                    <button 
                                                        onClick={() => handlePayoutAction(payout.id, 'reject')}
                                                        className="px-4 py-2 bg-red-100 hover:bg-red-200 text-red-600 rounded-lg font-bold flex items-center text-sm transition"
                                                    >
                                                        <FaBan className="mr-1" /> Reject
                                                    </button>
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Bank Details */}
                        <div className="bg-blue-50 p-6 rounded-2xl border border-blue-100">
                            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                                <FaIdCard className="mr-2 text-blue-600" /> Default Bank Account Details
                            </h3>
                            {rider.bank_details && Object.keys(rider.bank_details).length > 0 && rider.bank_details.bank_name ? (
                                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                                    <div>
                                        <label className="text-[10px] font-black text-gray-400 uppercase block mb-1">Bank Name</label>
                                        <p className="font-bold text-gray-800">{rider.bank_details.bank_name || 'N/A'}</p>
                                    </div>
                                    <div>
                                        <label className="text-[10px] font-black text-gray-400 uppercase block mb-1">Account Number</label>
                                        <p className="font-bold text-gray-800 font-mono">{rider.bank_details.account_number || 'N/A'}</p>
                                    </div>
                                    <div>
                                        <label className="text-[10px] font-black text-gray-400 uppercase block mb-1">IFSC Code</label>
                                        <p className="font-bold text-gray-800 font-mono">{rider.bank_details.ifsc_code || 'N/A'}</p>
                                    </div>
                                    <div>
                                        <label className="text-[10px] font-black text-gray-400 uppercase block mb-1">Holder Name</label>
                                        <p className="font-bold text-gray-800">{rider.bank_details.account_holder_name || 'N/A'}</p>
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
                                        <p className="font-mono font-medium text-gray-800">{rider.aadhar_number ? (`****${rider.aadhar_number.slice(-4)}`) : 'Not provided'}</p>
                                    </div>
                                    <div className="p-4 border rounded-xl bg-gray-50">
                                        <label className="text-xs font-bold text-gray-400 uppercase block mb-1">PAN Number</label>
                                        <p className="font-mono font-medium text-gray-800">{rider.pan_number ? (`****${rider.pan_number.slice(-4)}`) : 'Not provided'}</p>
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
