import { API_BASE_URL } from '../../config';

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import ProfileLayout from '../../components/ProfileLayout';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';

import { useAuth } from '../../contexts/AuthContext';

const AddressManagement = () => {
    const { token } = useAuth();
    const [addresses, setAddresses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingAddress, setEditingAddress] = useState(null);
    const [formData, setFormData] = useState({
        label: 'Home',
        address_line1: '',
        address_line2: '',
        landmark: '',
        city: '',
        state: '',
        pincode: '',
        is_default: false,
        latitude: 0,
        longitude: 0
    });

    const fetchAddresses = useCallback(async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/api/client/addresses/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
            });
            // Ensure we always get an array
            let data = res.data.results || res.data;
            // If data is not an array, set it to an empty array
            if (!Array.isArray(data)) {
                console.error('API returned non-array data:', data);
                data = [];
            }
            setAddresses(data);
        } catch (error) {
            console.error('Error fetching addresses:', error);
            toast.error('Failed to fetch addresses');
            setAddresses([]); // Set to empty array on error
        } finally {
            setLoading(false);
        }
    }, [token]);

    useEffect(() => {
        fetchAddresses();
    }, [fetchAddresses]);

    const handleOpenModal = (address = null) => {
        if (address) {
            setEditingAddress(address);
            setFormData(address);
        } else {
            setEditingAddress(null);
            setFormData({
                label: 'Home',
                address_line1: '',
                address_line2: '',
                landmark: '',
                city: '',
                state: '',
                pincode: '',
                is_default: false,
                latitude: 12.9716, // Default to some city coords for now
                longitude: 77.5946
            });
        }
        setIsModalOpen(true);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editingAddress) {
                await axios.put(`${API_BASE_URL}/api/client/addresses/${editingAddress.id}/`, formData, {
                    headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
                });
                toast.success('Address updated');
            } else {
                await axios.post(`${API_BASE_URL}/api/client/addresses/`, formData, {
                    headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
                });
                toast.success('New address added');
            }
            setIsModalOpen(false);
            fetchAddresses();
        } catch (error) {
            toast.error('Failed to save address');
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('Delete this address?')) {
            try {
                await axios.delete(`${API_BASE_URL}/api/client/addresses/${id}/`, {
                    headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
                });
                toast.success('Address deleted');
                fetchAddresses();
            } catch (error) {
                toast.error('Failed to delete address');
            }
        }
    };

    return (
        <ProfileLayout>
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-black text-gray-900">Manage Addresses</h1>
                    <p className="text-gray-500 font-medium">Add or edit your delivery locations</p>
                </div>
                <button
                    onClick={() => handleOpenModal()}
                    className="bg-red-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-red-700 transition-all shadow-lg hover:shadow-red-200"
                >
                    + Add New Address
                </button>
            </div>

            {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {[1, 2].map(i => <div key={i} className="h-48 bg-gray-200 animate-pulse rounded-2xl" />)}
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {addresses.map((addr) => (
                        <motion.div
                            key={addr.id}
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:border-red-200 hover:shadow-md transition-all group relative"
                        >
                            <div className="flex justify-between items-start mb-4">
                                <div className="flex items-center space-x-3">
                                    <span className="text-2xl">
                                        {addr.label === 'Home' ? '🏠' : addr.label === 'Work' ? '🏢' : '📍'}
                                    </span>
                                    <h3 className="text-lg font-black text-gray-900">{addr.label}</h3>
                                    {addr.is_default && (
                                        <span className="bg-red-50 text-red-600 text-[10px] font-black uppercase tracking-widest px-2 py-0.5 rounded border border-red-100">Default</span>
                                    )}
                                </div>
                                <div className="flex space-x-1">
                                    <button
                                        onClick={() => handleOpenModal(addr)}
                                        className="p-2 hover:bg-gray-50 rounded-lg text-gray-400 hover:text-red-600 transition-colors"
                                    >
                                        ✎
                                    </button>
                                    <button
                                        onClick={() => handleDelete(addr.id)}
                                        className="p-2 hover:bg-gray-50 rounded-lg text-gray-400 hover:text-red-600 transition-colors"
                                    >
                                        🗑
                                    </button>
                                </div>
                            </div>
                            <div className="space-y-1">
                                <p className="text-gray-800 font-medium leading-snug">{addr.address_line1}</p>
                                {addr.address_line2 && <p className="text-gray-500 text-sm">{addr.address_line2}</p>}
                                {addr.landmark && <p className="text-xs text-gray-400 italic">Landmark: {addr.landmark}</p>}
                                <p className="text-gray-500 font-bold text-sm">
                                    {addr.city}, {addr.state} - {addr.pincode}
                                </p>
                            </div>
                        </motion.div>
                    ))}
                </div>
            )}

            {/* Empty State */}
            {!loading && addresses.length === 0 && (
                <div className="bg-white rounded-3xl p-12 text-center border-2 border-dashed border-gray-200">
                    <div className="text-6xl mb-4">🏠</div>
                    <h2 className="text-2xl font-black text-gray-900 mb-2">No addresses found</h2>
                    <p className="text-gray-500 mb-8 max-w-xs mx-auto">Add your home or work address for faster checkouts</p>
                    <button
                        onClick={() => handleOpenModal()}
                        className="text-red-600 font-bold hover:underline"
                    >
                        Click here to add your first address
                    </button>
                </div>
            )}

            {/* Modal */}
            <AnimatePresence>
                {isModalOpen && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setIsModalOpen(false)}
                            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
                        />
                        <motion.div
                            initial={{ opacity: 0, y: 100, scale: 0.9 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: 100, scale: 0.9 }}
                            className="bg-white w-full max-w-lg rounded-3xl p-8 relative z-10 shadow-2xl"
                        >
                            <h2 className="text-2xl font-black text-gray-900 mb-6 flex items-center">
                                <span className="mr-3">{editingAddress ? '✎' : '📍'}</span>
                                {editingAddress ? 'Edit Address' : 'Add New Address'}
                            </h2>
                            <form onSubmit={handleSubmit} className="space-y-4">
                                <div>
                                    <label className="block text-xs font-black uppercase text-gray-400 mb-1 ml-1 tracking-widest">Address Label</label>
                                    <div className="flex space-x-2">
                                        {['Home', 'Work', 'Other'].map(label => (
                                            <button
                                                key={label}
                                                type="button"
                                                onClick={() => setFormData({ ...formData, label })}
                                                className={`flex-1 py-3 rounded-xl font-bold border-2 transition-all ${formData.label === label
                                                    ? 'bg-red-50 border-red-600 text-red-600'
                                                    : 'bg-white border-gray-100 text-gray-400 hover:border-gray-200'
                                                    }`}
                                            >
                                                {label}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                                <div className="space-y-4">
                                    <input
                                        type="text" required placeholder="Address Line 1"
                                        className="w-full px-5 py-3 rounded-xl border-2 border-gray-100 focus:border-red-600 outline-none font-medium transition-all"
                                        value={formData.address_line1}
                                        onChange={(e) => setFormData({ ...formData, address_line1: e.target.value })}
                                    />
                                    <input
                                        type="text" placeholder="Address Line 2 (Optional)"
                                        className="w-full px-5 py-3 rounded-xl border-2 border-gray-100 focus:border-red-600 outline-none font-medium transition-all"
                                        value={formData.address_line2}
                                        onChange={(e) => setFormData({ ...formData, address_line2: e.target.value })}
                                    />
                                    <div className="grid grid-cols-2 gap-4">
                                        <input
                                            type="text" placeholder="Landmark"
                                            className="w-full px-5 py-3 rounded-xl border-2 border-gray-100 focus:border-red-600 outline-none font-medium transition-all"
                                            value={formData.landmark}
                                            onChange={(e) => setFormData({ ...formData, landmark: e.target.value })}
                                        />
                                        <input
                                            type="text" placeholder="Pincode"
                                            className="w-full px-5 py-3 rounded-xl border-2 border-gray-100 focus:border-red-600 outline-none font-medium transition-all"
                                            value={formData.pincode}
                                            onChange={(e) => setFormData({ ...formData, pincode: e.target.value })}
                                        />
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <input
                                            type="text" placeholder="City"
                                            className="w-full px-5 py-3 rounded-xl border-2 border-gray-100 focus:border-red-600 outline-none font-medium transition-all"
                                            value={formData.city}
                                            onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                                        />
                                        <input
                                            type="text" placeholder="State"
                                            className="w-full px-5 py-3 rounded-xl border-2 border-gray-100 focus:border-red-600 outline-none font-medium transition-all"
                                            value={formData.state}
                                            onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                                        />
                                    </div>
                                </div>
                                <div className="flex items-center space-x-3 py-2 px-1">
                                    <input
                                        type="checkbox" id="is_default"
                                        className="h-5 w-5 rounded accent-red-600 focus:ring-red-600"
                                        checked={formData.is_default}
                                        onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
                                    />
                                    <label htmlFor="is_default" className="text-sm font-bold text-gray-700">Set as default address</label>
                                </div>
                                <div className="flex space-x-4 pt-4">
                                    <button
                                        type="button" onClick={() => setIsModalOpen(false)}
                                        className="flex-1 py-4 border-2 border-gray-100 rounded-2xl font-black text-gray-400 hover:bg-gray-50 transition-all"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        className="flex-[2] py-4 bg-red-600 text-white rounded-2xl font-black shadow-lg hover:shadow-red-200 transition-all"
                                    >
                                        {editingAddress ? 'Save Changes' : 'Add Address'}
                                    </button>
                                </div>
                            </form>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </ProfileLayout>
    );
};

export default AddressManagement;
