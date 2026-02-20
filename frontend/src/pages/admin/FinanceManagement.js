
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../config';
import toast from 'react-hot-toast';
import {
    FaWallet, FaHistory, FaFilter, FaSearch, FaArrowUp, FaArrowDown,
    FaUtensils, FaUser, FaCheckCircle, FaExclamationCircle, FaUndo
} from 'react-icons/fa';
import { format } from 'date-fns';

const FinanceManagement = () => {
    const [transactions, setTransactions] = useState([]);
    const [earnings, setEarnings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('transactions'); // 'transactions' or 'earnings'
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchData();
    }, [activeTab]);

    const fetchData = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token_admin');
            const endpoint = activeTab === 'transactions' ? 'wallet-transactions' : 'earnings';
            const res = await axios.get(`${API_BASE_URL}/api/admin/${endpoint}/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' }
            });
            const data = res.data.results ? res.data.results : res.data;
            if (activeTab === 'transactions') {
                setTransactions(Array.isArray(data) ? data : []);
            } else {
                setEarnings(Array.isArray(data) ? data : []);
            }
        } catch (error) {
            console.error(`Failed to fetch ${activeTab}`, error);
            toast.error(`Failed to load ${activeTab}`);
        } finally {
            setLoading(false);
        }
    };

    const filteredData = (activeTab === 'transactions' ? transactions : earnings).filter(item => {
        const searchInput = searchTerm.toLowerCase();
        if (activeTab === 'transactions') {
            return (
                item.user_name?.toLowerCase().includes(searchInput) ||
                item.description?.toLowerCase().includes(searchInput) ||
                item.source?.toLowerCase().includes(searchInput)
            );
        } else {
            return (
                item.restaurant_name?.toLowerCase().includes(searchInput) ||
                item.order_id_str?.toLowerCase().includes(searchInput)
            );
        }
    });

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-gray-800 flex items-center">
                <FaWallet className="mr-3 text-red-500" />
                Finance & Refunds
            </h1>

            {/* Tabs */}
            <div className="flex space-x-4 border-b border-gray-200">
                <button
                    onClick={() => setActiveTab('transactions')}
                    className={`pb-4 px-4 font-bold transition-all ${activeTab === 'transactions' ? 'text-red-500 border-b-2 border-red-500' : 'text-gray-400 hover:text-gray-600'}`}
                >
                    Wallet Transactions
                </button>
                <button
                    onClick={() => setActiveTab('earnings')}
                    className={`pb-4 px-4 font-bold transition-all ${activeTab === 'earnings' ? 'text-red-500 border-b-2 border-red-500' : 'text-gray-400 hover:text-gray-600'}`}
                >
                    Restaurant Earnings
                </button>
            </div>

            {/* Controls */}
            <div className="flex flex-col md:flex-row justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-gray-100 gap-4">
                <div className="relative w-full md:w-96">
                    <FaSearch className="absolute top-3.5 left-4 text-gray-400" />
                    <input
                        type="text"
                        placeholder={activeTab === 'transactions' ? "Search Customer, Description..." : "Search Restaurant, Order ID..."}
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-12 pr-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-red-500"
                    />
                </div>
            </div>

            {/* Content */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                {loading ? (
                    <div className="p-12 text-center text-gray-500 font-bold">Loading Data...</div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm text-gray-600">
                            {activeTab === 'transactions' ? (
                                <>
                                    <thead className="bg-gray-50 text-gray-800 uppercase tracking-wider font-bold">
                                        <tr>
                                            <th className="p-4">Date</th>
                                            <th className="p-4">Customer</th>
                                            <th className="p-4">Type</th>
                                            <th className="p-4">Source & Reason</th>
                                            <th className="p-4 text-right">Amount</th>
                                            <th className="p-4 text-right">New Balance</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-100">
                                        {filteredData.length > 0 ? (
                                            filteredData.map(tx => (
                                                <tr key={tx.id} className="hover:bg-gray-50 transition">
                                                    <td className="p-4 whitespace-nowrap">
                                                        {format(new Date(tx.created_at), 'MMM dd, yyyy HH:mm')}
                                                    </td>
                                                    <td className="p-4 font-bold text-gray-800">
                                                        {tx.user_name}
                                                    </td>
                                                    <td className="p-4">
                                                        <span className={`flex items-center gap-1 font-bold ${tx.transaction_type === 'CREDIT' ? 'text-green-600' : 'text-red-500'}`}>
                                                            {tx.transaction_type === 'CREDIT' ? <FaArrowUp /> : <FaArrowDown />}
                                                            {tx.transaction_type}
                                                        </span>
                                                    </td>
                                                    <td className="p-4">
                                                        <div className="font-bold text-gray-700">{tx.source}</div>
                                                        <div className="text-xs text-gray-400">{tx.description}</div>
                                                    </td>
                                                    <td className={`p-4 text-right font-black ${tx.transaction_type === 'CREDIT' ? 'text-green-600' : 'text-red-500'}`}>
                                                        {tx.transaction_type === 'CREDIT' ? '+' : '-'}₹{parseFloat(tx.amount).toLocaleString()}
                                                    </td>
                                                    <td className="p-4 text-right font-medium text-gray-500">
                                                        ₹{parseFloat(tx.balance_after).toLocaleString()}
                                                    </td>
                                                </tr>
                                            ))
                                        ) : (
                                            <tr><td colSpan="6" className="p-8 text-center text-gray-400">No transactions found.</td></tr>
                                        )}
                                    </tbody>
                                </>
                            ) : (
                                <>
                                    <thead className="bg-gray-50 text-gray-800 uppercase tracking-wider font-bold">
                                        <tr>
                                            <th className="p-4">Date</th>
                                            <th className="p-4">Restaurant</th>
                                            <th className="p-4 text-center">Order ID</th>
                                            <th className="p-4 text-right">Order Total</th>
                                            <th className="p-4 text-right">Commission</th>
                                            <th className="p-4 text-right">Payout (Net)</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-100">
                                        {filteredData.length > 0 ? (
                                            filteredData.map(earn => (
                                                <tr key={earn.id} className="hover:bg-gray-50 transition">
                                                    <td className="p-4 whitespace-nowrap">
                                                        {format(new Date(earn.created_at), 'MMM dd, yyyy')}
                                                    </td>
                                                    <td className="p-4 font-bold text-gray-800">
                                                        {earn.restaurant_name}
                                                    </td>
                                                    <td className="p-4 text-center">
                                                        <span className="bg-gray-100 px-2 py-1 rounded font-mono text-xs">#{earn.order_id_str}</span>
                                                    </td>
                                                    <td className="p-4 text-right font-medium">
                                                        ₹{parseFloat(earn.order_total).toLocaleString()}
                                                    </td>
                                                    <td className="p-4 text-right text-red-500 font-bold">
                                                        -₹{parseFloat(earn.commission).toLocaleString()}
                                                    </td>
                                                    <td className="p-4 text-right text-green-600 font-black">
                                                        ₹{parseFloat(earn.net_amount).toLocaleString()}
                                                    </td>
                                                </tr>
                                            ))
                                        ) : (
                                            <tr><td colSpan="6" className="p-8 text-center text-gray-400">No earnings data found.</td></tr>
                                        )}
                                    </tbody>
                                </>
                            )}
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default FinanceManagement;
