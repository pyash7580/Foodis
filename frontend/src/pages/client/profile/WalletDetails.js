import { API_BASE_URL } from '../../../config';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../../contexts/AuthContext';
import toast from 'react-hot-toast';

const WalletDetails = () => {
    const { token } = useAuth();
    const [wallet, setWallet] = useState(null);
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (token) {
            fetchWalletData();
        }
    }, [token]);

    const fetchWalletData = async () => {
        try {
            // Fetch wallet balance
            const walletRes = await axios.get(`${API_BASE_URL}/api/client/wallet/balance/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
            });
            setWallet(walletRes.data);

            // Fetch transactions
            const transRes = await axios.get(`${API_BASE_URL}/api/client/wallet/transactions/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
            });
            setTransactions(transRes.data);
            setLoading(false);
        } catch (error) {
            console.error("Wallet fetch error", error);
            // toast.error("Failed to load wallet data");
            setLoading(false);
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-400 font-bold">Loading Wallet...</div>;

    return (
        <div className="space-y-8">
            <header>
                <h1 className="text-2xl font-black text-gray-900">Foodis Wallet</h1>
                <p className="text-gray-500 mt-1">Manage your funds and view transaction history.</p>
            </header>

            {/* Balance Card */}
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-3xl p-8 text-white shadow-xl relative overflow-hidden">
                <div className="relative z-10">
                    <p className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-2">Available Balance</p>
                    <h2 className="text-5xl font-black tracking-tight flex items-baseline">
                        <span className="text-2xl mr-1">₹</span>
                        {wallet ? parseFloat(wallet.balance).toLocaleString('en-IN', { minimumFractionDigits: 2 }) : '0.00'}
                    </h2>
                    <p className="mt-4 text-gray-400 text-sm">
                        Use this balance to pay for orders seamlessly.
                    </p>
                </div>
                {/* Decorative */}
                <div className="absolute top-0 right-0 -mt-8 -mr-8 w-48 h-48 rounded-full bg-white/5 blur-3xl"></div>
                <div className="absolute bottom-0 left-0 -mb-8 -ml-8 w-48 h-48 rounded-full bg-red-500/10 blur-3xl"></div>
            </div>

            {/* Transactions */}
            <div>
                <h3 className="text-lg font-black text-gray-900 mb-6">Transaction History</h3>
                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
                    {transactions.length > 0 ? (
                        <div className="divide-y divide-gray-50">
                            {transactions.map(t => (
                                <div key={t.id} className="p-6 flex items-center justify-between hover:bg-gray-50 transition">
                                    <div className="flex items-center space-x-4">
                                        <div className={`h-12 w-12 rounded-xl flex items-center justify-center text-xl font-bold ${t.transaction_type === 'CREDIT' ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'}`}>
                                            {t.transaction_type === 'CREDIT' ? '⬇️' : '⬆️'}
                                        </div>
                                        <div>
                                            <p className="font-bold text-gray-900">{t.description || (t.transaction_type === 'CREDIT' ? 'Wallet Credit' : 'Payment for Order')}</p>
                                            <p className="text-xs text-gray-400 font-medium">
                                                {new Date(t.created_at).toLocaleDateString([], { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                                            </p>
                                        </div>
                                    </div>
                                    <div className={`text-right ${t.transaction_type === 'CREDIT' ? 'text-green-600' : 'text-gray-900'} font-black text-lg`}>
                                        {t.transaction_type === 'CREDIT' ? '+' : '-'}₹{Math.abs(t.amount)}
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="p-12 text-center text-gray-400 font-bold">
                            No transactions yet.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default WalletDetails;
