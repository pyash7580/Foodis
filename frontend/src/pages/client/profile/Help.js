import { API_BASE_URL } from '../../../config';
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuth } from '../../../contexts/AuthContext';

const Help = () => {
    const { token } = useAuth();
    const [view, setView] = useState('main'); // 'main', 'order_issues', 'payment_issues', 'account_issues'
    const [orders, setOrders] = useState([]);
    const [isChatOpen, setIsChatOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [chatMessages, setChatMessages] = useState([
        { type: 'bot', text: "Hi! I'm your Foodis Assistant. How can I help you today?" }
    ]);
    const [newMessage, setNewMessage] = useState('');

    const categories = [
        {
            id: 'order_issues',
            icon: '📦',
            title: 'I have a query related to an order',
            desc: 'Track order status, missing items, or delivery issues.',
            color: 'bg-blue-50 text-blue-600'
        },
        {
            id: 'payment_issues',
            icon: '💳',
            title: 'Payment & Wallet Issues',
            desc: 'Refund status, failed payments, or wallet balance queries.',
            color: 'bg-green-50 text-green-600'
        },
        {
            id: 'account_issues',
            icon: '👤',
            title: 'Account & Profile',
            desc: 'Update phone number, email issues, or login trouble.',
            color: 'bg-purple-100 text-purple-600'
        },
        {
            id: 'chat',
            icon: '💬',
            title: 'Chat with Verified Support',
            desc: 'Start a live chat with our customer support team.',
            color: 'bg-red-50 text-red-600'
        }
    ];

    const fetchOrders = async () => {
        if (!token) return;
        setLoading(true);
        try {
            const res = await axios.get(`${API_BASE_URL}/api/client/orders/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
            });
            if (res.data.results && Array.isArray(res.data.results)) {
                setOrders(res.data.results);
            } else if (Array.isArray(res.data)) {
                setOrders(res.data);
            } else {
                setOrders([]);
            }
        } catch (error) {
            toast.error("Failed to fetch orders for help");
        }
        setLoading(false);
    };

    const handleCategoryClick = (id) => {
        if (id === 'chat') {
            setIsChatOpen(true);
        } else if (id === 'order_issues') {
            setView('order_issues');
            fetchOrders();
        } else {
            setView(id);
        }
    };

    const handleSendMessage = (e) => {
        e.preventDefault();
        if (!newMessage.trim()) return;

        const userMsg = { type: 'user', text: newMessage };
        setChatMessages(prev => [...prev, userMsg]);
        setNewMessage('');

        setTimeout(() => {
            setChatMessages(prev => [...prev, {
                type: 'bot',
                text: "Thanks for sharing. A support executive will join this chat in about 2-3 minutes. Please stay connected."
            }]);
        }, 1000);
    };

    return (
        <div className="space-y-8">
            <header className="flex items-center space-x-4">
                {view !== 'main' && (
                    <button
                        onClick={() => setView('main')}
                        className="p-2 hover:bg-white rounded-full transition shadow-sm border border-gray-100"
                    >
                        <span className="text-xl">←</span>
                    </button>
                )}
                <div className="flex-1">
                    <header className="mb-12">
                        <h1 className="text-4xl font-black text-gray-900 mb-2">Help Center</h1>
                        <p className="text-gray-500 font-bold mb-6">How can we help you today?</p>

                        {/* Direct Contact Info */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-red-50 p-6 rounded-3xl border border-red-100 shadow-sm">
                            <a href="tel:+919824948665" className="flex items-center space-x-4 group">
                                <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center text-xl shadow-sm group-hover:scale-110 transition">📞</div>
                                <div>
                                    <p className="text-[10px] font-black uppercase tracking-widest text-red-400">Call Us Directly</p>
                                    <p className="text-gray-900 font-bold">+91 9824948665</p>
                                </div>
                            </a>
                            <a href="mailto:foodis4785@gmail.com" className="flex items-center space-x-4 group">
                                <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center text-xl shadow-sm group-hover:scale-110 transition">📧</div>
                                <div>
                                    <p className="text-[10px] font-black uppercase tracking-widest text-red-400">Email Support</p>
                                    <p className="text-gray-900 font-bold">foodis4785@gmail.com</p>
                                </div>
                            </a>
                        </div>
                    </header>
                </div>
            </header>

            <AnimatePresence mode="wait">
                {view === 'main' && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="grid grid-cols-1 md:grid-cols-2 gap-6"
                    >
                        {categories.map(cat => (
                            <button
                                key={cat.id}
                                onClick={() => handleCategoryClick(cat.id)}
                                className="bg-white p-6 rounded-[2rem] shadow-sm border border-gray-100 flex items-start text-left hover:border-red-500 hover:shadow-xl hover:shadow-red-50 transition-all duration-300 group"
                            >
                                <div className={`h-14 w-14 ${cat.color} rounded-2xl flex items-center justify-center text-2xl mr-5 group-hover:scale-110 transition-transform`}>
                                    {cat.icon}
                                </div>
                                <div className="flex-1">
                                    <h3 className="font-black text-gray-900 mb-1">{cat.title}</h3>
                                    <p className="text-xs text-gray-400 font-bold leading-relaxed">{cat.desc}</p>
                                </div>
                            </button>
                        ))}
                    </motion.div>
                )}

                {view === 'order_issues' && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                        <h3 className="text-lg font-black text-gray-900 mb-4">Select an order for help</h3>
                        {loading ? (
                            <div className="py-12 text-center text-gray-400 font-bold italic animate-pulse">Loading orders...</div>
                        ) : (
                            <div className="grid grid-cols-1 gap-4">
                                {orders.map(order => (
                                    <button
                                        key={order.id}
                                        onClick={() => toast.success(`Issue for Order #${order.order_id} logged!`)}
                                        className="w-full bg-white p-5 rounded-2xl border border-gray-100 flex items-center justify-between hover:border-red-400 transition"
                                    >
                                        <div className="flex items-center space-x-4">
                                            <div className="h-10 w-10 bg-gray-50 rounded-lg flex items-center justify-center text-lg">🥡</div>
                                            <div className="text-left">
                                                <p className="font-black text-gray-900 text-sm">Order #{order.order_id}</p>
                                                <p className="text-[10px] text-gray-400 font-bold uppercase">₹{order.total} • {new Date(order.placed_at).toLocaleDateString()}</p>
                                            </div>
                                        </div>
                                        <span className="px-2 py-1 bg-red-50 text-red-600 rounded text-[10px] font-black uppercase tracking-widest">{order.status}</span>
                                    </button>
                                ))}
                            </div>
                        )}
                    </motion.div>
                )}

                {view === 'payment_issues' && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-white p-10 rounded-[2.5rem] border border-gray-100 text-center">
                        <div className="text-5xl mb-6">💳</div>
                        <h3 className="text-2xl font-black text-gray-900 mb-4">Payment & Wallet</h3>
                        <p className="text-gray-500 mb-8 max-w-sm mx-auto font-medium">Having trouble with a refund or a failed payment? Our experts are ready to audit your transactions.</p>
                        <button
                            onClick={() => setIsChatOpen(true)}
                            className="bg-black text-white px-10 py-4 rounded-2xl font-black text-sm shadow-xl hover:scale-105 transition-transform"
                        >
                            Start Payment Audit Chat
                        </button>
                    </motion.div>
                )}

                {view === 'account_issues' && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {[
                                { t: 'Change Phone Number', d: 'Update contact info' },
                                { t: 'Deactivate Account', d: 'Request deletion' },
                                { t: 'Email Issues', d: 'OTP not received' },
                                { t: 'Login Trouble', d: 'Verification issues' }
                            ].map((item, id) => (
                                <button key={id} onClick={() => toast.success(item.t + " flow starting...")} className="p-6 bg-white border border-gray-100 rounded-2xl text-left hover:border-red-500 transition-all group">
                                    <p className="font-black text-gray-800 group-hover:text-red-600 transition-colors">{item.t}</p>
                                    <p className="text-xs text-gray-400 font-bold mt-1 uppercase tracking-tight">{item.d}</p>
                                </button>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Chat Modal */}
            <AnimatePresence>
                {isChatOpen && (
                    <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-[200] flex items-center justify-center p-4">
                        <motion.div
                            initial={{ y: 50, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            exit={{ y: 50, opacity: 0 }}
                            className="bg-white w-full max-w-md h-[600px] rounded-[3rem] shadow-2xl overflow-hidden flex flex-col"
                        >
                            <div className="bg-red-600 p-8 text-white flex justify-between items-center">
                                <div className="flex items-center space-x-4">
                                    <div className="h-12 w-12 bg-white/20 rounded-2xl flex items-center justify-center text-2xl">👤</div>
                                    <div>
                                        <p className="font-black text-lg">Support Agent</p>
                                        <div className="flex items-center text-[10px] font-bold uppercase tracking-widest opacity-80">
                                            <span className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></span> Online
                                        </div>
                                    </div>
                                </div>
                                <button onClick={() => setIsChatOpen(false)} className="h-10 w-10 bg-white/10 rounded-full flex items-center justify-center hover:bg-white/20 transition-colors">✕</button>
                            </div>

                            <div className="flex-1 overflow-y-auto p-8 space-y-6 bg-gray-50/50">
                                {chatMessages.map((msg, idx) => (
                                    <div key={idx} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                                        <div className={`max-w-[85%] px-5 py-3 rounded-2xl text-sm font-bold shadow-sm ${msg.type === 'user' ? 'bg-red-600 text-white rounded-br-none' : 'bg-white text-gray-800 rounded-bl-none border border-gray-100'}`}>
                                            {msg.text}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <form onSubmit={handleSendMessage} className="p-6 bg-white border-t border-gray-100">
                                <div className="flex space-x-3">
                                    <input
                                        type="text"
                                        value={newMessage}
                                        onChange={(e) => setNewMessage(e.target.value)}
                                        placeholder="Explain your problem..."
                                        className="flex-1 bg-gray-50 rounded-2xl px-5 py-4 text-sm font-bold focus:outline-none focus:ring-4 ring-red-50 transition-all"
                                    />
                                    <button
                                        type="submit"
                                        className="h-14 w-14 bg-red-600 text-white rounded-2xl flex items-center justify-center shadow-lg shadow-red-100 hover:scale-105 active:scale-95 transition-all"
                                    >
                                        📤
                                    </button>
                                </div>
                            </form>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default Help;
