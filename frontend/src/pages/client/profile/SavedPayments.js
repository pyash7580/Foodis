import { API_BASE_URL } from '../../../config';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

import { useAuth } from '../../../contexts/AuthContext';

const SavedPayments = () => {
    const { token } = useAuth();
    const [payments, setPayments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [formData, setFormData] = useState({
        cardNumber: '',
        cardHolder: '',
        expiry: '',
        cvv: ''
    });

    useEffect(() => {
        if (token) {
            fetchPayments();
        }
    }, [token]);

    const fetchPayments = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/api/client/saved-payments/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
            });
            // Handle paginated response
            const data = res.data.results || res.data;
            setPayments(Array.isArray(data) ? data : []);
        } catch (error) {
            toast.error("Failed to load payment methods");
        } finally {
            setLoading(false);
        }
    };

    const detectBrand = (number) => {
        if (number.startsWith('4')) return 'Visa';
        if (number.startsWith('5')) return 'Mastercard';
        return 'Card';
    };

    const handleAddCard = async (e) => {
        e.preventDefault();

        // Basic Validation
        const cleanNumber = formData.cardNumber.replace(/\s/g, '');
        if (cleanNumber.length !== 16) {
            toast.error("Invalid card number");
            return;
        }
        if (!/^\d{2}\/\d{2}$/.test(formData.expiry)) {
            toast.error("Expiry must be MM/YY");
            return;
        }

        const [mm, yy] = formData.expiry.split('/');
        const fullExpiry = `${mm}/20${yy}`;

        const payload = {
            method_type: 'CARD',
            card_brand: detectBrand(cleanNumber),
            card_last4: cleanNumber.slice(-4),
            card_expiry: fullExpiry,
            is_default: payments.length === 0
        };

        const loadingToast = toast.loading("Adding card...");
        try {
            await axios.post(`${API_BASE_URL}/api/client/saved-payments/`, payload, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
            });
            toast.success("Card added successfully!", { id: loadingToast });
            setShowModal(false);
            setFormData({ cardNumber: '', cardHolder: '', expiry: '', cvv: '' });
            fetchPayments();
        } catch (error) {
            toast.error("Failed to add card", { id: loadingToast });
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Remove this payment method?")) return;
        try {
            await axios.delete(`${API_BASE_URL}/api/client/saved-payments/${id}/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
            });
            toast.success("Payment method removed");
            fetchPayments();
        } catch (error) {
            toast.error("Failed to remove payment method");
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-400 font-bold">Loading Payments...</div>;

    return (
        <div className="space-y-8 relative">
            <header className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-black text-gray-900">Saved Payment Methods</h1>
                    <p className="text-gray-500 mt-1">Manage your saved cards and UPI IDs for faster checkout.</p>
                </div>
                <button
                    onClick={() => setShowModal(true)}
                    className="bg-red-600 text-white font-black hover:bg-red-700 px-6 py-3 rounded-2xl shadow-lg transition-all active:scale-95"
                >
                    + Add New Card
                </button>
            </header>

            {/* Modal */}
            {showModal && (
                <div className="fixed inset-0 z-[2000] flex items-center justify-center p-4">
                    <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setShowModal(false)} />
                    <div className="bg-white rounded-3xl p-8 max-w-md w-full relative z-10 shadow-2xl">
                        <h2 className="text-2xl font-black text-gray-900 mb-6">Add New Card</h2>
                        <form onSubmit={handleAddCard} className="space-y-4">
                            <div>
                                <label className="block text-xs font-black text-gray-400 uppercase mb-2">Card Number</label>
                                <input
                                    type="text"
                                    maxLength="16"
                                    placeholder="0000 0000 0000 0000"
                                    className="w-full bg-gray-50 border-none rounded-xl px-4 py-3 font-bold focus:ring-2 ring-red-500"
                                    value={formData.cardNumber}
                                    onChange={e => setFormData({ ...formData, cardNumber: e.target.value.replace(/\D/g, '') })}
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-black text-gray-400 uppercase mb-2">Card Holder Name</label>
                                <input
                                    type="text"
                                    placeholder="JOHN DOE"
                                    className="w-full bg-gray-50 border-none rounded-xl px-4 py-3 font-bold focus:ring-2 ring-red-500"
                                    value={formData.cardHolder}
                                    onChange={e => setFormData({ ...formData, cardHolder: e.target.value.toUpperCase() })}
                                    required
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs font-black text-gray-400 uppercase mb-2">Expiry (MM/YY)</label>
                                    <input
                                        type="text"
                                        placeholder="MM/YY"
                                        maxLength="5"
                                        className="w-full bg-gray-50 border-none rounded-xl px-4 py-3 font-bold focus:ring-2 ring-red-500 text-center"
                                        value={formData.expiry}
                                        onChange={e => {
                                            let val = e.target.value.replace(/\D/g, '');
                                            if (val.length > 2) val = val.slice(0, 2) + '/' + val.slice(2);
                                            setFormData({ ...formData, expiry: val });
                                        }}
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-black text-gray-400 uppercase mb-2">CVV</label>
                                    <input
                                        type="password"
                                        placeholder="•••"
                                        maxLength="3"
                                        className="w-full bg-gray-50 border-none rounded-xl px-4 py-3 font-bold focus:ring-2 ring-red-500 text-center"
                                        value={formData.cvv}
                                        onChange={e => setFormData({ ...formData, cvv: e.target.value.replace(/\D/g, '') })}
                                        required
                                    />
                                </div>
                            </div>
                            <div className="pt-4 flex space-x-3">
                                <button type="button" onClick={() => setShowModal(false)} className="flex-1 bg-gray-100 text-gray-500 font-bold py-3 rounded-xl hover:bg-gray-200 transition">Cancel</button>
                                <button type="submit" className="flex-1 bg-red-600 text-white font-black py-3 rounded-xl shadow-lg hover:bg-red-700 transition">Save Card</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {Array.isArray(payments) && payments.map(method => (
                    <div key={method.id} className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-between group">
                        <div className="flex items-center space-x-4">
                            <div className="h-12 w-16 bg-gray-100 rounded-lg flex items-center justify-center text-2xl">
                                {method.method_type === 'CARD' ? '💳' : '📱'}
                            </div>
                            <div>
                                <p className="font-bold text-gray-900">
                                    {method.method_type === 'CARD' ? method.card_brand || 'Card' : 'UPI ID'}
                                </p>
                                <p className="text-gray-500 text-sm font-mono tracking-wider">
                                    {method.method_type === 'CARD' ? `•••• ${method.card_last4}` : method.upi_id}
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={() => handleDelete(method.id)}
                            className="text-gray-400 hover:text-red-500 font-bold text-sm px-3 py-1 rounded-lg hover:bg-red-50 transition"
                        >
                            Remove
                        </button>
                    </div>
                ))}

                {payments.length === 0 && (
                    <div className="col-span-2 text-center py-12 bg-white rounded-3xl border border-dashed border-gray-200">
                        <p className="text-gray-400 font-bold">No saved payment methods.</p>
                        <p className="text-xs text-gray-400 mt-1">Save a card or UPI ID during checkout for faster payments.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SavedPayments;
