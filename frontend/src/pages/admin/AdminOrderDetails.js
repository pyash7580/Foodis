
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../config';
import { FaTimes, FaShoppingBag, FaMapMarkerAlt, FaTruck, FaClock, FaTimesCircle } from 'react-icons/fa';

import { format } from 'date-fns';

const AdminOrderDetails = ({ orderId, onClose }) => {
    const [order, setOrder] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDetails = async () => {
            try {
                const token = localStorage.getItem('token_admin');
                const res = await axios.get(`${API_BASE_URL}/api/admin/orders/${orderId}/`, {
                    headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' }
                });
                setOrder(res.data);
            } catch (error) {
                console.error("Failed to fetch order details", error);
            } finally {
                setLoading(false);
            }
        };

        if (orderId) fetchDetails();
    }, [orderId]);

    if (!orderId) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl">
                <div className="p-6 border-b flex justify-between items-center sticky top-0 bg-white z-10">
                    <h2 className="text-2xl font-bold text-gray-800 flex items-center">
                        <FaShoppingBag className="mr-3 text-red-500" />
                        View Order
                    </h2>
                    <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full transition">
                        <FaTimes className="text-xl text-gray-500" />
                    </button>
                </div>

                {loading ? (
                    <div className="p-12 text-center text-gray-500">Loading details...</div>
                ) : order ? (
                    <div className="p-6 space-y-8">
                        {/* Summary Header */}
                        <div className="flex flex-col md:flex-row justify-between gap-6 border-b pb-6">
                            <div>
                                <h1 className="text-3xl font-black text-gray-900 mb-1">#{order.order_id}</h1>
                                <p className="text-gray-500 flex items-center">
                                    <FaClock className="mr-2" />
                                    {format(new Date(order.placed_at), 'MMMM dd, yyyy • hh:mm a')}
                                </p>
                            </div>
                            <div className="text-right">
                                <span className={`px-4 py-2 rounded-full text-sm font-black uppercase tracking-widest ${order.status === 'DELIVERED' ? 'bg-green-100 text-green-700' :
                                    order.status === 'CANCELLED' ? 'bg-red-100 text-red-700' :
                                        'bg-blue-100 text-blue-700'
                                    }`}>
                                    {order.status}
                                </span>
                                <p className="mt-2 text-xs font-bold text-gray-400 uppercase tracking-widest">
                                    Payment: <span className={order.payment_status === 'PAID' ? 'text-green-600' : 'text-red-500'}>{order.payment_status}</span> • {order.payment_method}
                                </p>
                            </div>
                        </div>

                        {/* Customer & Restaurant Info */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="bg-gray-50 p-6 rounded-2xl border border-gray-100">
                                <h3 className="text-sm font-black text-gray-400 uppercase mb-4 flex items-center">
                                    <FaMapMarkerAlt className="mr-2 text-blue-500" /> Delivery To
                                </h3>
                                <div className="space-y-2">
                                    <p className="font-bold text-lg text-gray-800">{order.user_name}</p>
                                    <p className="text-gray-600 leading-relaxed italic">{order.delivery_address}</p>
                                </div>
                            </div>

                            <div className="bg-gray-50 p-6 rounded-2xl border border-gray-100">
                                <h3 className="text-sm font-black text-gray-400 uppercase mb-4 flex items-center">
                                    <FaTruck className="mr-2 text-red-500" /> Picking From
                                </h3>
                                <div className="space-y-4">
                                    <div>
                                        <p className="font-bold text-lg text-gray-800">{order.restaurant_name}</p>
                                        <p className="text-xs text-gray-400 uppercase">Assigned Rider: <span className="text-gray-700 font-bold">{order.rider_name || 'Not Assigned'}</span></p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Order Items */}
                        <div className="bg-white border border-gray-100 rounded-2xl overflow-hidden shadow-sm">
                            <div className="bg-gray-50 px-6 py-4 border-b border-gray-100">
                                <h3 className="font-bold text-gray-800">Order Items</h3>
                            </div>
                            <div className="divide-y divide-gray-100">
                                {order.items && order.items.map((item, idx) => (
                                    <div key={idx} className="p-6 flex justify-between items-center group hover:bg-gray-50 transition">
                                        <div className="flex items-center gap-4">
                                            <div className="w-10 h-10 bg-red-50 rounded-lg flex items-center justify-center text-red-500 font-bold text-lg">
                                                {item.quantity}x
                                            </div>
                                            <div>
                                                <p className="font-bold text-gray-800">{item.menu_item_name}</p>
                                                {item.customizations && Object.keys(item.customizations).length > 0 && (
                                                    <p className="text-xs text-gray-400 italic">Customized</p>
                                                )}
                                            </div>
                                        </div>
                                        <p className="font-bold text-gray-800">₹{parseFloat(item.subtotal).toLocaleString()}</p>
                                    </div>
                                ))}
                            </div>

                            {/* Detailed Bill */}
                            <div className="bg-gray-900 text-white p-8">
                                <div className="space-y-4 max-w-xs ml-auto">
                                    <div className="flex justify-between text-sm text-gray-400">
                                        <span>Subtotal</span>
                                        <span>₹{parseFloat(order.subtotal).toLocaleString()}</span>
                                    </div>
                                    <div className="flex justify-between text-sm text-gray-400">
                                        <span>Delivery Fee</span>
                                        <span>₹{parseFloat(order.delivery_fee).toLocaleString()}</span>
                                    </div>
                                    {parseFloat(order.discount) > 0 && (
                                        <div className="flex justify-between text-sm text-red-400">
                                            <span>Discount</span>
                                            <span>-₹{parseFloat(order.discount).toLocaleString()}</span>
                                        </div>
                                    )}
                                    <div className="flex justify-between text-sm text-gray-400">
                                        <span>Tax</span>
                                        <span>₹{parseFloat(order.tax).toLocaleString()}</span>
                                    </div>
                                    <div className="pt-4 border-t border-gray-800 flex justify-between items-center text-xl font-black">
                                        <span>Total</span>
                                        <span className="text-red-500">₹{parseFloat(order.total).toLocaleString()}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                    </div>
                ) : (
                    <div className="p-12 text-center text-red-500 font-bold flex flex-col items-center">
                        <FaTimesCircle className="text-4xl mb-4" />
                        Detailed information not available.
                    </div>
                )}

                <div className="p-6 border-t bg-gray-50 flex justify-end">
                    <button
                        onClick={onClose}
                        className="w-full sm:w-auto px-8 py-3 bg-gray-900 text-white rounded-xl font-black uppercase tracking-widest text-xs hover:bg-gray-800 transition shadow-lg text-center"
                    >
                        Close View
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AdminOrderDetails;
