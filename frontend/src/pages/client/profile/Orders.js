import { API_BASE_URL } from '../../../config';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../../../contexts/AuthContext';
import { useCart } from '../../../contexts/CartContext';

const Orders = () => {
    const { token } = useAuth();
    const { addToCart, cartItems, restaurant: cartRestaurant, clearCart } = useCart();
    const navigate = useNavigate();
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedOrder, setSelectedOrder] = useState(null);

    useEffect(() => {
        if (token) {
            fetchOrders();
        }
    }, [token]);

    const fetchOrders = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/api/client/orders/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
            });
            // Handle paginated response
            if (res.data.results && Array.isArray(res.data.results)) {
                setOrders(res.data.results);
            } else if (Array.isArray(res.data)) {
                setOrders(res.data);
            } else {
                setOrders([]);
            }
            setLoading(false);
        } catch (error) {
            console.error("Orders fetch error", error);
            setLoading(false);
        }
    };

    const handleReorder = (order) => {
        if (!order.items || order.items.length === 0) {
            toast.error("Cannot reorder: No items found in this order");
            return;
        }

        // Check if we are switching restaurants
        const orderRestaurant = order.restaurant;
        if (cartRestaurant && cartRestaurant.id !== orderRestaurant.id) {
            if (!window.confirm("Start a new basket? Reordering from a different restaurant will clear your current cart.")) {
                return;
            }
            clearCart(); // Clear cart once here
        }

        // Add each item to cart
        order.items.forEach(item => {
            addToCart(item.menu_item, orderRestaurant, item.quantity, item.customizations || {});
        });

        toast.success("Items added to cart!");
        navigate('/client/cart');
    };

    const handleDownloadInvoice = async (orderId) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/client/orders/${orderId}/invoice/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' },
                responseType: 'blob' // Important for PDF download
            });

            // Create blob link to download
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Invoice_${orderId}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);

            toast.success('Invoice downloaded successfully!');
        } catch (error) {
            console.error('Invoice download error:', error);
            toast.error('Failed to download invoice');
        }
    };

    const [showCancelModal, setShowCancelModal] = useState(false);
    const [cancelOrderId, setCancelOrderId] = useState(null);
    const [cancelReason, setCancelReason] = useState('Changed my mind');
    const [customReason, setCustomReason] = useState('');

    const CANCEL_REASONS = [
        "Changed my mind",
        "Ordered by mistake",
        "Delivery time is too long",
        "Found a better price",
        "Other"
    ];

    const handleCancelClick = (orderId) => {
        setCancelOrderId(orderId);
        setShowCancelModal(true);
        setCancelReason('Changed my mind'); // Reset to default
        setCustomReason('');
    };

    const submitCancellation = async () => {
        const finalReason = cancelReason === 'Other' ? customReason : cancelReason;
        if (!finalReason) {
            toast.error("Please provide a reason");
            return;
        }

        const toastId = toast.loading("Cancelling order...");
        try {
            const res = await axios.post(`${API_BASE_URL}/api/client/orders/${cancelOrderId}/cancel/`,
                { reason: finalReason },
                { headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' } }
            );

            // Handle new response format
            const successMsg = res.data.message || "Order cancelled successfully";
            toast.success(successMsg, { id: toastId });

            setShowCancelModal(false);
            fetchOrders(); // Refresh status

            // Optional: Show refund info if available
            if (res.data.order?.payment_status === 'REFUNDED') {
                toast("Refund credited to your wallet", { icon: '💰' });
            }
        } catch (error) {
            console.error("Cancel Error:", error);
            // Handle structured error from backend
            const errorData = error.response?.data;
            const errorMsg = errorData?.error || errorData?.detail || error.message || "Failed to cancel order";

            // If we have specific details (in DEBUG mode), log them
            if (errorData?.details) {
                console.error("Server Details:", errorData.details);
            }

            toast.error(`Error: ${errorMsg}`, { id: toastId, duration: 5000 });
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-400 font-bold">Loading Orders...</div>;

    return (
        <div className="space-y-8 relative">
            <header>
                <h1 className="text-2xl font-black text-gray-900">Order History</h1>
            </header>

            <div className="space-y-6">
                {Array.isArray(orders) && orders.map(order => (
                    <div key={order.id} className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 transition hover:shadow-md">
                        <div className="flex flex-col sm:flex-row justify-between sm:items-start mb-4 gap-4 sm:gap-0">
                            <div className="flex items-start sm:items-center space-x-4">
                                <div className="h-12 w-12 sm:h-16 sm:w-16 bg-gray-100 rounded-xl flex items-center justify-center text-xl sm:text-2xl flex-shrink-0">
                                    🥡
                                </div>
                                <div>
                                    <h3 className="font-black text-gray-900 text-base sm:text-lg leading-tight">
                                        {order.restaurant?.name || 'Restaurant'}
                                    </h3>
                                    <p className="text-gray-500 text-xs mt-1">
                                        {order.items?.map(i => `${i.quantity}x ${i.menu_item?.name || 'Item'}`).join(', ').substring(0, 50)}...
                                    </p>
                                    <p className="text-gray-400 text-[10px] font-bold uppercase tracking-widest mt-2">
                                        ORDER #{order.order_id} • {new Date(order.placed_at).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                                    </p>
                                </div>
                            </div>
                            <div className="text-left sm:text-right flex flex-row sm:flex-col items-center sm:items-end justify-between sm:justify-start w-full sm:w-auto mt-2 sm:mt-0 pt-3 sm:pt-0 border-t sm:border-0 border-gray-50">
                                <span className={`px-3 py-1.5 sm:py-1 rounded-lg text-[10px] sm:text-xs font-black uppercase tracking-widest ${order.status === 'DELIVERED' ? 'bg-green-50 text-green-600' : order.status === 'CANCELLED' ? 'bg-red-50 text-red-600' : 'bg-gray-100 text-gray-600'}`}>
                                    {order.status}
                                </span>
                                <p className="font-black text-gray-900 mt-0 sm:mt-2 text-lg sm:text-base">₹{order.total}</p>
                            </div>
                        </div>

                        <div className="flex flex-wrap sm:flex-nowrap justify-end gap-2 sm:gap-0 sm:space-x-3 pt-4 border-t border-gray-50">
                            {['PENDING', 'CONFIRMED'].includes(order.status) && (
                                <button onClick={() => handleCancelClick(order.order_id)} className="w-full sm:w-auto text-red-500 font-bold text-sm px-4 py-2 hover:bg-red-50 rounded-xl transition border border-transparent hover:border-red-100">
                                    Cancel
                                </button>
                            )}

                            {['PENDING', 'CONFIRMED', 'PREPARING', 'READY', 'ASSIGNED', 'PICKED_UP', 'ON_THE_WAY'].includes(order.status) && (
                                <Link to={`/client/track/${order.order_id}`} className="w-full sm:w-auto bg-red-50 text-red-600 font-bold text-sm px-4 py-2 rounded-xl border border-red-100 hover:bg-red-100 transition flex items-center justify-center">
                                    <span className="mr-2 animate-pulse">●</span> Track
                                </Link>
                            )}
                            <button onClick={() => setSelectedOrder(order)} className="flex-1 sm:flex-none text-gray-600 font-bold text-sm px-4 py-2 bg-gray-50 sm:bg-transparent hover:bg-gray-100 rounded-xl transition text-center">
                                Details
                            </button>
                            <button onClick={() => handleReorder(order)} className="flex-1 sm:flex-none bg-red-600 text-white font-bold text-sm px-4 py-2 rounded-xl shadow-lg shadow-red-100 hover:bg-red-700 transition text-center">
                                Reorder
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Cancel Order Modal */}
            {showCancelModal && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
                    <div className="bg-white w-full max-w-md rounded-3xl overflow-hidden shadow-2xl animate-in zoom-in-95 duration-200">
                        <div className="p-6 border-b border-gray-50">
                            <h3 className="font-black text-xl text-gray-900">Cancel Order?</h3>
                            <p className="text-gray-500 text-sm mt-1">Please select a reason for cancellation.</p>
                        </div>
                        <div className="p-6 space-y-3">
                            {CANCEL_REASONS.map((reason) => (
                                <label key={reason} className={`flex items-center p-3 rounded-xl border cursor-pointer transition ${cancelReason === reason ? 'border-red-500 bg-red-50' : 'border-gray-200 hover:border-gray-300'}`}>
                                    <input
                                        type="radio"
                                        name="cancelReason"
                                        value={reason}
                                        checked={cancelReason === reason}
                                        onChange={(e) => setCancelReason(e.target.value)}
                                        className="w-4 h-4 text-red-600 focus:ring-red-500"
                                    />
                                    <span className={`ml-3 font-bold ${cancelReason === reason ? 'text-red-700' : 'text-gray-700'}`}>{reason}</span>
                                </label>
                            ))}

                            {cancelReason === 'Other' && (
                                <textarea
                                    value={customReason}
                                    onChange={(e) => setCustomReason(e.target.value)}
                                    placeholder="Tell us why..."
                                    className="w-full mt-2 p-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 ring-red-500 text-sm font-medium"
                                    rows="3"
                                />
                            )}
                        </div>
                        <div className="p-6 bg-gray-50 flex gap-4">
                            <button onClick={() => setShowCancelModal(false)} className="flex-1 py-3 text-gray-600 font-bold hover:bg-gray-200 rounded-xl transition">
                                Don't Cancel
                            </button>
                            <button onClick={submitCancellation} className="flex-1 py-3 bg-red-600 text-white font-bold rounded-xl shadow-lg shadow-red-200 hover:bg-red-700 transition">
                                Confirm Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Order Details Modal */}
            {selectedOrder && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
                    <div className="bg-white w-full max-w-lg rounded-3xl overflow-hidden shadow-2xl animate-in zoom-in-95 duration-200">
                        <div className="p-6 border-b border-gray-50 flex justify-between items-center bg-gray-50/50">
                            <div>
                                <h3 className="font-black text-lg text-gray-900">Order Summary</h3>
                                <p className="text-xs text-gray-500 font-bold uppercase tracking-widest">#{selectedOrder.order_id}</p>
                            </div>
                            <button onClick={() => setSelectedOrder(null)} className="text-gray-400 hover:text-gray-900 text-xl">✕</button>
                        </div>
                        <div className="p-6 max-h-[60vh] overflow-y-auto">
                            <div className="space-y-4">
                                {selectedOrder.items && selectedOrder.items.map((item, idx) => (
                                    <div key={idx} className="flex justify-between items-center text-sm">
                                        <div className="flex items-center space-x-2">
                                            <span className="font-bold text-gray-900">{item.quantity}x</span>
                                            <span className="text-gray-600 font-medium">{item.menu_item?.name || 'Item'}</span>
                                        </div>
                                        <span className="font-bold text-gray-900">₹{item.subtotal}</span>
                                    </div>
                                ))}

                                <div className="border-t border-dashed border-gray-200 my-4 pt-4 space-y-2">
                                    <div className="flex justify-between text-xs text-gray-500 font-bold">
                                        <span>Item Total</span>
                                        <span>₹{selectedOrder.subtotal}</span>
                                    </div>
                                    <div className="flex justify-between text-xs text-gray-500 font-bold">
                                        <span>Delivery Fee</span>
                                        <span>₹{selectedOrder.delivery_fee}</span>
                                    </div>
                                    <div className="flex justify-between text-xs text-gray-500 font-bold">
                                        <span>Taxes & Charges</span>
                                        <span>₹{selectedOrder.tax}</span>
                                    </div>
                                    <div className="flex justify-between text-lg font-black text-gray-900 pt-2 border-t border-gray-100">
                                        <span>Total</span>
                                        <span>₹{selectedOrder.total}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="mt-6 bg-gray-50 p-4 rounded-xl">
                                <p className="text-xs text-gray-400 font-black uppercase tracking-widest mb-1">Items delivered to</p>
                                <p className="text-sm font-bold text-gray-900">{selectedOrder.delivery_address}</p>
                            </div>

                            {selectedOrder.status === 'CANCELLED' && selectedOrder.cancellation_reason && (
                                <div className="mt-4 bg-red-50 p-4 rounded-xl border border-red-100">
                                    <p className="text-xs text-red-400 font-black uppercase tracking-widest mb-1">Cancellation Reason</p>
                                    <p className="text-sm font-bold text-red-900">{selectedOrder.cancellation_reason}</p>
                                </div>
                            )}
                        </div>
                        {selectedOrder.status === 'DELIVERED' && (
                            <div className="p-6 bg-gray-50 border-t border-gray-100">
                                <button
                                    onClick={() => handleDownloadInvoice(selectedOrder.order_id)}
                                    className="w-full py-3 bg-red-600 text-white rounded-xl font-bold hover:bg-red-700 hover:shadow-lg transition"
                                >
                                    📄 Download Invoice
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Orders;
