import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const RestaurantOrderDetailsModal = ({ order, onClose }) => {
    if (!order) return null;

    const getStatusColor = (status) => {
        const colors = {
            PENDING: 'bg-yellow-100 text-yellow-800',
            CONFIRMED: 'bg-blue-100 text-blue-800',
            PREPARING: 'bg-purple-100 text-purple-800',
            READY: 'bg-indigo-100 text-indigo-800',
            PICKED_UP: 'bg-orange-100 text-orange-800',
            DELIVERED: 'bg-green-100 text-green-800',
            CANCELLED: 'bg-red-100 text-red-800',
        };
        return colors[status] || 'bg-gray-100';
    };

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose}
                    className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                ></motion.div>

                <motion.div
                    initial={{ scale: 0.95, opacity: 0, y: 20 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    exit={{ scale: 0.95, opacity: 0, y: 20 }}
                    className="relative bg-white w-full max-w-4xl rounded-[2.5rem] shadow-2xl overflow-hidden max-h-[90vh] flex flex-col"
                >
                    {/* Header */}
                    <div className="p-8 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                        <div>
                            <div className="flex items-center space-x-3 mb-2">
                                <h2 className="text-3xl font-black text-gray-900 tracking-tight">#{order.order_id}</h2>
                                <span className={`px-3 py-1 rounded-full text-xs font-black uppercase tracking-widest ${getStatusColor(order.status)}`}>
                                    {order.status}
                                </span>
                            </div>
                            <p className="text-sm font-bold text-gray-400 uppercase tracking-widest">
                                Placed at {new Date(order.placed_at).toLocaleString()}
                            </p>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-3 bg-white rounded-full hover:bg-gray-100 transition shadow-sm border border-gray-100"
                        >
                            ❌
                        </button>
                    </div>

                    {/* Content - Scrollable */}
                    <div className="p-8 overflow-y-auto flex-1 custom-scrollbar">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
                            {/* Left Column: Order Items */}
                            <div className="md:col-span-2 space-y-8">
                                {order.pickup_otp && (
                                    <div className="bg-gradient-to-r from-red-500 to-orange-500 p-6 rounded-3xl text-white shadow-lg shadow-red-200 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                                        <div>
                                            <p className="font-bold text-white/80 text-xs uppercase tracking-widest mb-1">Rider Verification Code</p>
                                            <h3 className="text-4xl font-black tracking-widest bg-white/20 inline-block px-4 py-1 rounded-xl backdrop-blur-md border border-white/20">
                                                {order.pickup_otp}
                                            </h3>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-xs font-bold text-white/80 uppercase tracking-widest">Status</p>
                                            <p className="text-lg font-black">Awaiting Pickup</p>
                                        </div>
                                    </div>
                                )}

                                <div>
                                    <h3 className="text-lg font-black text-gray-900 mb-6 uppercase tracking-widest flex items-center">
                                        <span className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center mr-3 text-sm">🛒</span>
                                        Order Items
                                    </h3>
                                    <div className="space-y-4">
                                        {order.items.map((item, idx) => (
                                            <div key={idx} className="flex justify-between items-start p-4 bg-gray-50 rounded-2xl border border-gray-100">
                                                <div className="flex items-start space-x-4">
                                                    <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center font-black text-gray-400 border border-gray-100 shadow-sm">
                                                        {item.quantity}x
                                                    </div>
                                                    <div>
                                                        <h4 className="font-bold text-gray-900">{item.menu_item_name}</h4>
                                                        {item.customizations && Object.keys(item.customizations).length > 0 && (
                                                            <div className="mt-1 flex flex-wrap gap-1">
                                                                {Object.entries(item.customizations).map(([key, val]) => (
                                                                    <span key={key} className="text-[10px] font-bold bg-white text-gray-500 px-2 py-0.5 rounded border border-gray-200">
                                                                        {val}
                                                                    </span>
                                                                ))}
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                                <p className="font-black text-gray-900">₹{item.subtotal}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Bill Details */}
                                <div className="bg-gray-50 p-6 rounded-3xl border border-gray-100 space-y-3">
                                    <div className="flex justify-between text-sm font-bold text-gray-500">
                                        <span>Item Total</span>
                                        <span>₹{order.subtotal}</span>
                                    </div>
                                    <div className="flex justify-between text-sm font-bold text-gray-500">
                                        <span>Tax</span>
                                        <span>₹{order.tax}</span>
                                    </div>
                                    <div className="flex justify-between text-sm font-bold text-gray-500">
                                        <span>Delivery Fee</span>
                                        <span>₹{order.delivery_fee}</span>
                                    </div>
                                    <div className="flex justify-between text-sm font-bold text-gray-500">
                                        <span>Discount</span>
                                        <span className="text-green-500">-₹{order.discount}</span>
                                    </div>
                                    <div className="h-px bg-gray-200 my-2"></div>
                                    <div className="flex justify-between text-xl font-black text-gray-900">
                                        <span>Grand Total</span>
                                        <span>₹{order.total}</span>
                                    </div>
                                    <div className="bg-white p-3 rounded-xl border border-gray-200 text-center text-xs font-black uppercase tracking-widest text-gray-500 mt-4">
                                        Payment: <span className={order.payment_status === 'PAID' ? 'text-green-500' : 'text-orange-500'}>{order.payment_status}</span> via {order.payment_method}
                                    </div>
                                </div>
                            </div>

                            {/* Right Column: Customer & Delivery */}
                            <div className="space-y-8">
                                <div>
                                    <h3 className="text-lg font-black text-gray-900 mb-6 uppercase tracking-widest flex items-center">
                                        <span className="w-8 h-8 rounded-full bg-blue-100/50 text-blue-600 flex items-center justify-center mr-3 text-sm">👤</span>
                                        Customer
                                    </h3>
                                    <div className="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm space-y-4">
                                        <div>
                                            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Name</p>
                                            <p className="font-black text-gray-900 text-lg">{order.user_name}</p>
                                        </div>
                                        <div>
                                            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Phone</p>
                                            <p className="font-bold text-gray-700">{order.user_phone}</p>
                                        </div>
                                        <div>
                                            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Delivery Address</p>
                                            <p className="font-medium text-gray-600 text-sm leading-relaxed bg-gray-50 p-3 rounded-xl border border-gray-100">
                                                {order.delivery_address}
                                            </p>
                                        </div>
                                        {order.delivery_instructions && (
                                            <div>
                                                <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Instructions</p>
                                                <p className="font-medium text-orange-600 text-sm bg-orange-50 p-3 rounded-xl border border-orange-100">
                                                    "{order.delivery_instructions}"
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {order.rider && (
                                    <div>
                                        <h3 className="text-lg font-black text-gray-900 mb-6 uppercase tracking-widest flex items-center">
                                            <span className="w-8 h-8 rounded-full bg-indigo-100/50 text-indigo-600 flex items-center justify-center mr-3 text-sm">🛵</span>
                                            Rider
                                        </h3>
                                        <div className="bg-indigo-50 p-6 rounded-3xl border border-indigo-100 space-y-4">
                                            <div className="flex items-center space-x-4">
                                                <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center text-xl shadow-sm">
                                                    🧑‍🚀
                                                </div>
                                                <div>
                                                    <p className="font-black text-gray-900">{order.rider_name}</p>
                                                    <p className="text-xs font-bold text-indigo-500 uppercase tracking-widest">Assigned Partner</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default RestaurantOrderDetailsModal;
