import { API_BASE_URL } from '../../config';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ProfileLayout from '../../components/ProfileLayout';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

import { useAuth } from '../../contexts/AuthContext';

const Wallet = () => {
    const { token } = useAuth();
    const [wallet, setWallet] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchWallet = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/api/client/wallet/balance/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
            });
            setWallet(res.data);
        } catch (error) {
            toast.error('Failed to fetch wallet contents');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (token) {
            fetchWallet();
        }
    }, [token]);

    if (loading) return <ProfileLayout><div className="animate-pulse h-64 bg-gray-200 rounded-3xl" /></ProfileLayout>;

    return (
        <ProfileLayout>
            <div className="mb-8">
                <h1 className="text-3xl font-black text-gray-900">Foodis Wallet</h1>
                <p className="text-gray-500 font-medium">Manage your credits and refunds</p>
            </div>

            {/* Balance Card */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-red-600 rounded-3xl p-10 text-white shadow-xl relative overflow-hidden mb-12"
            >
                <div className="absolute top-0 right-0 p-12 opacity-10 text-8xl">💳</div>
                <div className="relative z-10">
                    <p className="text-red-100 font-bold uppercase tracking-widest text-xs mb-2">Available Balance</p>
                    <div className="text-6xl font-black mb-6">₹{Math.max(0, parseFloat(wallet?.balance || 0)).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                    <div className="flex space-x-4">
                        <button className="bg-white text-red-600 px-8 py-3 rounded-xl font-black shadow-lg hover:bg-red-50 transition-all">
                            Add Money
                        </button>
                        <button className="bg-red-700/50 backdrop-blur-md text-white px-8 py-3 rounded-xl font-bold hover:bg-red-700/70 transition-all">
                            Transfer
                        </button>
                    </div>
                </div>
            </motion.div>

            {/* Transaction History */}
            <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="px-8 py-6 border-b border-gray-50 flex items-center justify-between">
                    <h2 className="text-xl font-black text-gray-900">Transaction History</h2>
                    <span className="text-xs bg-gray-100 text-gray-500 font-bold px-3 py-1 rounded-full">{wallet?.transactions?.length || 0} Records</span>
                </div>

                <div className="divide-y divide-gray-50">
                    {wallet?.transactions?.length > 0 ? (
                        wallet.transactions.map((tx, idx) => (
                            <motion.div
                                key={tx.id}
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: idx * 0.05 }}
                                className="px-8 py-5 flex items-center justify-between hover:bg-gray-50/50 transition-colors"
                            >
                                <div className="flex items-center space-x-5">
                                    <div className={`h-12 w-12 rounded-2xl flex items-center justify-center text-xl shadow-sm ${tx.transaction_type === 'CREDIT' ? 'bg-green-100' : 'bg-red-50'
                                        }`}>
                                        {tx.source === 'REFUND' ? '🔄' : tx.source === 'ORDER_PAYMENT' ? '🍔' : '💸'}
                                    </div>
                                    <div>
                                        <p className="font-bold text-gray-900 leading-tight">
                                            {tx.source.replace('_', ' ')}
                                        </p>
                                        <p className="text-xs text-gray-400 font-medium">
                                            {new Date(tx.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}
                                        </p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className={`text-lg font-black ${tx.transaction_type === 'CREDIT' ? 'text-green-600' : 'text-gray-900'
                                        }`}>
                                        {tx.transaction_type === 'CREDIT' ? '+' : '-'} ₹{tx.amount}
                                    </p>
                                    <p className="text-[10px] text-gray-400 font-black uppercase tracking-tighter">
                                        After: ₹{tx.balance_after}
                                    </p>
                                </div>
                            </motion.div>
                        ))
                    ) : (
                        <div className="p-20 text-center">
                            <div className="text-5xl mb-4">🙊</div>
                            <p className="text-gray-400 font-bold">No transactions yet</p>
                        </div>
                    )}
                </div>
            </div>
        </ProfileLayout>
    );
};

export default Wallet;
