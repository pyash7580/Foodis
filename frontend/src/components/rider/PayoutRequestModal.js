import React, { useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../../config';
import { motion, AnimatePresence } from 'framer-motion';
import { FaTimes, FaMoneyBillWave, FaUniversity, FaCreditCard, FaCheckCircle } from 'react-icons/fa';

const PayoutRequestModal = ({ isOpen, onClose, walletBalance, onSuccess }) => {
    const [amount, setAmount] = useState(walletBalance || '');
    const [method, setMethod] = useState('UPI');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    // Form states
    const [upiId, setUpiId] = useState('');
    const [accountName, setAccountName] = useState('');
    const [bankName, setBankName] = useState('');
    const [accountNumber, setAccountNumber] = useState('');
    const [ifscCode, setIfscCode] = useState('');
    const [cardNumber, setCardNumber] = useState('');
    const [cardName, setCardName] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        
        const reqAmount = parseFloat(amount);
        if (isNaN(reqAmount) || reqAmount < 1000) {
            setError('Minimum payout amount is ₹1000');
            return;
        }
        if (reqAmount > walletBalance) {
            setError('Amount exceeds your wallet balance');
            return;
        }

        let details = {};
        if (method === 'UPI') {
            if (!upiId) return setError('UPI ID is required');
            details = { upi_id: upiId };
        } else if (method === 'BANK') {
            if (!accountName || !bankName || !accountNumber || !ifscCode) return setError('All bank details are required');
            details = { account_name: accountName, bank_name: bankName, account_number: accountNumber, ifsc_code: ifscCode };
        } else if (method === 'CARD') {
            if (!cardNumber || !cardName) return setError('Card details are required');
            details = { card_number: cardNumber, card_name: cardName };
        }

        setLoading(true);
        try {
            const token = localStorage.getItem('token_rider');
            const res = await axios.post(`${API_BASE_URL}/api/rider/earnings/request_payout/`, {
                amount: reqAmount,
                payout_method: method,
                payout_details: details
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });
            
            setSuccess(true);
            setTimeout(() => {
                onSuccess(res.data.new_balance);
                onClose();
                setSuccess(false);
            }, 2000);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to request payout');
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                <motion.div 
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="bg-[#1A1F2C] border border-white/10 w-full max-w-md rounded-3xl overflow-hidden shadow-2xl relative"
                >
                    <div className="p-6 border-b border-white/5 flex justify-between items-center">
                        <h2 className="text-xl font-bold text-white">Request Payout</h2>
                        <button onClick={onClose} className="p-2 text-gray-400 hover:text-white rounded-full hover:bg-white/5 transition-colors">
                            <FaTimes />
                        </button>
                    </div>

                    <div className="p-6">
                        {success ? (
                            <div className="text-center py-8">
                                <motion.div 
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    className="w-20 h-20 bg-emerald-500/20 text-emerald-500 rounded-full flex items-center justify-center mx-auto mb-4"
                                >
                                    <FaCheckCircle className="text-4xl" />
                                </motion.div>
                                <h3 className="text-2xl font-bold text-white mb-2">Request Sent!</h3>
                                <p className="text-gray-400">Your payout of ₹{amount} has been requested successfully.</p>
                            </div>
                        ) : (
                            <form onSubmit={handleSubmit} className="space-y-6">
                                <div>
                                    <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Amount to Withdraw</label>
                                    <div className="relative">
                                        <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 font-bold">₹</span>
                                        <input 
                                            type="number" 
                                            value={amount}
                                            onChange={(e) => setAmount(e.target.value)}
                                            className="w-full bg-black/30 border border-white/10 rounded-xl py-3 pl-8 pr-4 text-white font-bold focus:outline-none focus:border-emerald-500"
                                            placeholder="Minimum ₹1000"
                                            min="1000"
                                            max={walletBalance}
                                        />
                                    </div>
                                    <p className="text-xs text-emerald-500 mt-2">Available: ₹{walletBalance}</p>
                                </div>

                                <div>
                                    <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Payout Method</label>
                                    <div className="grid grid-cols-3 gap-2">
                                        {[
                                            { id: 'UPI', icon: FaMoneyBillWave, label: 'UPI' },
                                            { id: 'BANK', icon: FaUniversity, label: 'Bank' },
                                            { id: 'CARD', icon: FaCreditCard, label: 'Card' }
                                        ].map(m => (
                                            <button 
                                                type="button"
                                                key={m.id}
                                                onClick={() => setMethod(m.id)}
                                                className={`p-3 rounded-xl border flex flex-col items-center justify-center space-y-2 transition-all ${method === m.id ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400' : 'bg-white/5 border-white/5 text-gray-400 hover:bg-white/10'}`}
                                            >
                                                <m.icon className="text-xl" />
                                                <span className="text-xs font-bold">{m.label}</span>
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    {method === 'UPI' && (
                                        <input 
                                            type="text" 
                                            value={upiId}
                                            onChange={(e) => setUpiId(e.target.value)}
                                            placeholder="Enter UPI ID (e.g. name@okhdfcbank)"
                                            className="w-full bg-black/30 border border-white/10 rounded-xl py-3 px-4 text-white font-bold focus:outline-none focus:border-emerald-500"
                                        />
                                    )}

                                    {method === 'BANK' && (
                                        <>
                                            <input type="text" value={accountName} onChange={(e) => setAccountName(e.target.value)} placeholder="Account Holder Name" className="w-full bg-black/30 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-emerald-500" />
                                            <input type="text" value={bankName} onChange={(e) => setBankName(e.target.value)} placeholder="Bank Name" className="w-full bg-black/30 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-emerald-500" />
                                            <input type="text" value={accountNumber} onChange={(e) => setAccountNumber(e.target.value)} placeholder="Account Number" className="w-full bg-black/30 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-emerald-500" />
                                            <input type="text" value={ifscCode} onChange={(e) => setIfscCode(e.target.value)} placeholder="IFSC Code" className="w-full bg-black/30 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-emerald-500" />
                                        </>
                                    )}

                                    {method === 'CARD' && (
                                        <>
                                            <input type="text" value={cardName} onChange={(e) => setCardName(e.target.value)} placeholder="Name on Card" className="w-full bg-black/30 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-emerald-500" />
                                            <input type="text" value={cardNumber} onChange={(e) => setCardNumber(e.target.value)} placeholder="Card Number" className="w-full bg-black/30 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-emerald-500" />
                                        </>
                                    )}
                                </div>

                                {error && <p className="text-red-500 text-sm text-center font-bold">{error}</p>}

                                <button 
                                    type="submit"
                                    disabled={loading}
                                    className="w-full bg-emerald-500 hover:bg-emerald-600 text-white font-bold py-4 rounded-xl transition-colors disabled:opacity-50"
                                >
                                    {loading ? 'Processing...' : 'Submit Request'}
                                </button>
                            </form>
                        )}
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default PayoutRequestModal;
