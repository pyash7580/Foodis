import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';
import { FaBox, FaClock, FaMapMarkerAlt, FaMotorcycle, FaHistory, FaChevronRight } from 'react-icons/fa';
import { useRider } from '../../contexts/RiderContext';
import { useAuth } from '../../contexts/AuthContext';
import { API_BASE_URL, WS_BASE_URL } from '../../config';
import { toast } from 'react-hot-toast';

const RiderOrders = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const { headers, isOnline } = useRider();
    const [activeTab, setActiveTab] = useState('available');
    const [availableOrders, setAvailableOrders] = useState([]);
    const [activeOrder, setActiveOrder] = useState(null);
    const [orderHistory, setOrderHistory] = useState([]);
    const [loading, setLoading] = useState(false);

    // WebSocket refs
    const ws = useRef(null);

    const fetchOrders = useCallback(async () => {
        setLoading(true);
        try {
            const timestamp = new Date().getTime();
            if (activeTab === 'available') {
                const res = await axios.get(`${API_BASE_URL}/api/rider/orders/available/?_t=${timestamp}`, { headers });
                setAvailableOrders(res.data);
            } else if (activeTab === 'active' || activeTab === 'accepted') {
                const res = await axios.get(`${API_BASE_URL}/api/rider/orders/active/?_t=${timestamp}`, { headers });
                setActiveOrder(res.data);
            } else if (activeTab === 'history') {
                const res = await axios.get(`${API_BASE_URL}/api/rider/orders/history/?_t=${timestamp}`, { headers });
                setOrderHistory(res.data.results || res.data);
            }
        } catch (err) {
            console.error("Failed to fetch orders", err);
        } finally {
            setLoading(false);
        }
    }, [activeTab, headers]);

    // Initial Fetch
    useEffect(() => {
        fetchOrders();
    }, [fetchOrders, activeTab, isOnline]);

    // WebSocket for Available Orders
    useEffect(() => {
        if (!isOnline || activeTab !== 'available') return;

        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = WS_BASE_URL || `${wsProtocol}//${window.location.hostname}:8000/ws`;

        if (user && user.id) {
            const socketUrl = `${wsUrl}/notifications/${user.id}/`;
            ws.current = new WebSocket(socketUrl);

            ws.current.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.message && (data.message.type === 'order_assigned' || data.message.type === 'new_order')) {
                    fetchOrders();
                }
            };

            return () => {
                if (ws.current) ws.current.close();
            };
        }
    }, [isOnline, activeTab, user, fetchOrders]);

    const handleAccept = async (orderId) => {
        try {
            await axios.post(`${API_BASE_URL}/api/rider/orders/${orderId}/accept/`, {}, { headers });
            toast.success("Order Accepted!");
            setActiveTab('active');
        } catch (err) {
            toast.error("Failed to accept. It might be taken.");
            fetchOrders();
        }
    };

    const handleReject = async (orderId) => {
        try {
            await axios.post(`${API_BASE_URL}/api/rider/orders/${orderId}/reject/`, {}, { headers });
            setAvailableOrders(prev => prev.filter(o => (o.order?.id || o.id) !== orderId));
            toast.success("Order Hidden");
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div className="flex flex-col space-y-8 animate-in fade-in duration-500">
            {/* Header */}
            <div className="flex flex-col space-y-2">
                <h1 className="text-3xl font-black text-white tracking-tight">Delivery Hub</h1>
                <p className="text-xs text-gray-500 font-bold uppercase tracking-[0.2em]">{activeTab} Deliveries</p>
            </div>

            {/* Navigation Tabs */}
            <div className="flex p-1.5 bg-white/5 rounded-[2rem] border border-white/5 w-fit">
                {['available', 'active', 'history'].map(tab => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`px-8 py-3 rounded-[1.5rem] text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === tab
                            ? 'bg-[#FF3008] text-white shadow-[0_10px_20px_rgba(255,48,8,0.2)]'
                            : 'text-gray-500 hover:text-white'
                            }`}
                    >
                        {tab}
                    </button>
                ))}
            </div>

            {/* Content Area */}
            <div className="min-h-[400px]">
                {loading && (
                    <div className="flex justify-center p-20">
                        <div className="w-8 h-8 border-2 border-t-[#FF3008] border-white/5 rounded-full animate-spin"></div>
                    </div>
                )}

                {!loading && activeTab === 'available' && (
                    <AvailableOrdersList
                        orders={availableOrders}
                        onAccept={handleAccept}
                        onReject={handleReject}
                        isOnline={isOnline}
                    />
                )}

                {!loading && activeTab === 'active' && (
                    <ActiveOrderView order={activeOrder} navigate={navigate} />
                )}

                {!loading && activeTab === 'history' && (
                    <OrderHistoryList orders={orderHistory} />
                )}
            </div>
        </div>
    );
};

const AvailableOrdersList = ({ orders, onAccept, onReject, isOnline }) => {
    if (!isOnline) {
        return (
            <div className="text-center py-20 px-6 opacity-50">
                <FaMotorcycle className="mx-auto text-4xl mb-4 text-gray-600" />
                <h3 className="text-lg font-bold">You are Offline</h3>
                <p className="text-xs text-gray-400 mt-2">Go online to receive orders.</p>
            </div>
        );
    }

    if (orders.length === 0) {
        return (
            <div className="text-center py-20 px-6 opacity-50">
                <div className="relative w-16 h-16 mx-auto mb-4">
                    <div className="absolute inset-0 bg-emerald-500/20 rounded-full animate-ping"></div>
                    <div className="relative bg-emerald-500/10 rounded-full w-full h-full flex items-center justify-center">
                        <FaClock className="text-emerald-500" />
                    </div>
                </div>
                <h3 className="text-lg font-bold">Searching...</h3>
                <p className="text-xs text-gray-400 mt-2">Looking for orders near you</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {orders.map((item) => {
                const order = item.order || item; // Handle wrapped or direct object
                const distance = item.distance;
                const earnings = item.estimated_earning || '40+'; // Fallback

                return (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        key={order.id}
                        className="glass-card p-5 rounded-3xl border border-white/5 relative overflow-hidden"
                    >
                        <div className="absolute top-0 right-0 w-20 h-20 bg-emerald-500/10 rounded-full blur-2xl -mr-10 -mt-10"></div>

                        <div className="relative z-10">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h3 className="font-black text-white text-lg">{order.restaurant_name}</h3>
                                    <p className="text-[10px] text-gray-400 uppercase tracking-wider">{order.restaurant_address}</p>
                                </div>
                                <div className="text-right">
                                    <div className="text-emerald-400 font-black text-xl">₹{Math.round(earnings)}</div>
                                    <div className="text-[9px] text-gray-500 uppercase tracking-widest">Est. Earnings</div>
                                </div>
                            </div>

                            <div className="flex items-center space-x-4 mb-6 text-xs text-gray-300">
                                <div className="flex items-center bg-white/5 px-3 py-1.5 rounded-lg">
                                    <FaMapMarkerAlt className="mr-2 text-orange-400" />
                                    <span>{distance ? `${distance} km` : 'Near'}</span>
                                </div>
                                <div className="flex items-center bg-white/5 px-3 py-1.5 rounded-lg">
                                    <FaBox className="mr-2 text-blue-400" />
                                    <span>{order.items?.length || 1} Items</span>
                                </div>
                            </div>

                            <div className="flex space-x-3">
                                <button
                                    onClick={() => onReject(order.id)}
                                    className="flex-1 py-3 rounded-xl bg-white/5 text-gray-400 font-black text-[10px] uppercase tracking-widest hover:bg-white/10 transition-colors"
                                >
                                    Ignore
                                </button>
                                <button
                                    onClick={() => onAccept(order.id)}
                                    className="flex-[2] py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-black text-[10px] uppercase tracking-widest shadow-lg active:scale-95 transition-transform"
                                >
                                    Accept Order
                                </button>
                            </div>
                        </div>
                    </motion.div>
                );
            })}
        </div>
    );
};

const ActiveOrderView = ({ order, navigate }) => {
    const { headers } = useRider(); // We need headers here for actions
    const [otp, setOtp] = useState('');
    const [localLoading, setLocalLoading] = useState(false);
    const [currentOrder, setCurrentOrder] = useState(order);

    // Sync prop changes
    useEffect(() => {
        setCurrentOrder(order);
    }, [order]);

    // Refresh handler
    const fetchOrderDetails = async () => {
        try {
            const timestamp = new Date().getTime();
            const res = await axios.get(`${API_BASE_URL}/api/rider/orders/${currentOrder.id}/?_t=${timestamp}`, { headers });
            setCurrentOrder(res.data);
        } catch (err) {
            console.error("Failed to refresh order", err);
        }
    };

    if (!currentOrder) {
        return (
            <div className="text-center py-20 px-6 opacity-50">
                <FaBox className="mx-auto text-4xl mb-4 text-gray-600" />
                <h3 className="text-lg font-bold">No Active Order</h3>
                <p className="text-xs text-gray-400 mt-2">Accept an order to start delivering.</p>
            </div>
        );
    }

    const isPickupPhase = ['ASSIGNED', 'ACCEPTED', 'READY', 'PREPARING', 'CONFIRMED'].includes(currentOrder.status);
    const isPickedUp = currentOrder.status === 'PICKED_UP';
    const isDeliveryPhase = currentOrder.status === 'ON_THE_WAY';

    const arrivedAtRestaurant = async () => {
        setLocalLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/api/rider/orders/${currentOrder.id}/arrived_at_restaurant/`, {}, { headers });
            toast.success("Marked as Arrived at Restaurant");
            fetchOrderDetails();
            fetchOrderDetails();
        } catch (err) {
            console.error("Arrival Error:", err);
            const errorMsg = err.response?.data?.error || "Action failed";
            toast.error(errorMsg);
        }
        finally { setLocalLoading(false); }
    };

    const startDelivery = async () => {
        setLocalLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/api/rider/orders/${currentOrder.id}/start_delivery/`, {}, { headers });
            toast.success("Delivery Started! Ride safe 🛵");
            fetchOrderDetails();
        } catch (err) {
            console.error("Start Delivery Error:", err);
            const errorMsg = err.response?.data?.error || "Action failed";
            toast.error(errorMsg);
        }
        finally { setLocalLoading(false); }
    };

    const arrivedAtCustomer = async () => {
        setLocalLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/api/rider/orders/${currentOrder.id}/arrived_at_customer/`, {}, { headers });
            toast.success("Marked as Arrived at Customer");
            fetchOrderDetails();
            fetchOrderDetails();
        } catch (err) {
            console.error("Arrival Customer Error:", err);
            const errorMsg = err.response?.data?.error || "Action failed";
            toast.error(errorMsg);
        }
        finally { setLocalLoading(false); }
    };

    const handlePickup = async () => {
        if (otp.length !== 6) return toast.error("Enter 6-digit Pickup OTP");
        setLocalLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/api/rider/orders/${currentOrder.id}/pickup/`, { otp }, { headers });
            toast.success("Order Picked Up!");
            setOtp('');
            fetchOrderDetails();
        } catch (err) {
            const errorMsg = err.response?.data?.error || "Invalid OTP or Failed to Pickup";
            toast.error(errorMsg);
        } finally { setLocalLoading(false); }
    };

    const handleDelivery = async () => {
        if (otp.length !== 6) return toast.error("Enter 6-digit Delivery OTP");
        setLocalLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/api/rider/orders/${currentOrder.id}/deliver/`, { otp }, { headers });
            toast.success("Order Delivered Successfully!");
            // navigate('/rider/orders'); // Refresh or move to history?
            window.location.reload(); // Simple reload to reset state to available or empty
        } catch (err) {
            const errorMsg = err.response?.data?.error || "Invalid OTP or Failed to Deliver";
            toast.error(errorMsg);
        } finally { setLocalLoading(false); }
    };

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card p-6 rounded-[2.5rem] border border-emerald-500/20 relative overflow-hidden"
        >
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-500 to-teal-500"></div>

            <div className="flex justify-between items-center mb-6">
                <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border ${isPickupPhase ? 'bg-orange-500/10 text-orange-400 border-orange-500/20' : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'}`}>
                    {isPickupPhase ? 'Pickup Phase' : 'Delivery Phase'}
                </span>
                <span className="text-[10px] text-gray-400 font-bold uppercase">#{currentOrder.id}</span>
            </div>

            {/* Restaurant Info */}
            <div className={`mb-6 p-4 rounded-2xl border border-white/5 ${isPickupPhase ? 'bg-white/5' : 'opacity-50'}`}>
                <h2 className="text-xl font-black text-white mb-1">{currentOrder.restaurant_name}</h2>
                <p className="text-xs text-gray-400 mb-2">{currentOrder.restaurant_address}</p>
                {isPickupPhase && (
                    <div className="mt-4">
                        <button
                            onClick={arrivedAtRestaurant}
                            disabled={localLoading}
                            className="w-full bg-[#FF3008]/20 text-[#FF3008] border border-[#FF3008]/50 py-3 rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-[#FF3008]/30 transition-all mb-3"
                        >
                            Mark Arrived
                        </button>
                        <div className="flex space-x-2">
                            <input
                                type="text"
                                value={otp}
                                onChange={e => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                                className="flex-1 bg-black/40 border border-white/10 rounded-xl px-4 py-3 font-black text-center tracking-[0.5em] text-white focus:border-orange-500 outline-none"
                                placeholder="******"
                            />
                            <button
                                onClick={handlePickup}
                                disabled={localLoading || otp.length < 6}
                                className="px-6 bg-[#FF3008] text-white rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-orange-600 disabled:opacity-50"
                            >
                                Verify
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {/* Delivery Actions */}
            {(isPickedUp || isDeliveryPhase) && (
                <div className="mt-4 p-4 rounded-2xl border border-white/5 bg-white/5">
                    <h2 className="text-xl font-black text-white mb-1">{currentOrder.customer_name}</h2>
                    <p className="text-xs text-gray-400 mb-4">{currentOrder.customer_address}</p>

                    {isPickedUp && (
                        <button
                            onClick={startDelivery}
                            disabled={localLoading}
                            className="w-full bg-blue-600 text-white py-4 rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-blue-700 transition-all mb-3 shadow-lg"
                        >
                            Start Delivery trip
                        </button>
                    )}

                    {isDeliveryPhase && (
                        <div className="space-y-4">
                            <button
                                onClick={arrivedAtCustomer}
                                disabled={localLoading}
                                className="w-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/50 py-3 rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-emerald-500/30 transition-all mb-3"
                            >
                                Mark Arrived
                            </button>
                            <div className="flex space-x-2">
                                <input
                                    type="text"
                                    value={otp}
                                    onChange={e => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                                    className="flex-1 bg-black/40 border border-white/10 rounded-xl px-4 py-3 font-black text-center tracking-[0.5em] text-white focus:border-emerald-500 outline-none"
                                    placeholder="******"
                                />
                                <button
                                    onClick={handleDelivery}
                                    disabled={localLoading || otp.length < 6}
                                    className="px-6 bg-emerald-500 text-white rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-emerald-600 disabled:opacity-50"
                                >
                                    Deliver
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            )}

            <button
                onClick={() => navigate(`/rider/order/${currentOrder.id}`)}
                className="w-full mt-6 py-4 rounded-2xl bg-white/5 text-gray-400 font-bold text-[10px] uppercase tracking-[0.2em] flex items-center justify-center space-x-2 hover:bg-white/10 transition-colors border border-white/5"
            >
                <span>View Full Details & Map</span>
                <FaChevronRight />
            </button>
        </motion.div>
    );
};

const OrderHistoryList = ({ orders }) => {
    if (orders.length === 0) {
        return (
            <div className="text-center py-20 px-6 opacity-50">
                <FaHistory className="mx-auto text-4xl mb-4 text-gray-600" />
                <h3 className="text-lg font-bold">No History</h3>
                <p className="text-xs text-gray-400 mt-2">Completed orders will appear here.</p>
            </div>
        );
    }

    return (
        <div className="space-y-3">
            {orders.map((order) => (
                <div key={order.id} className="glass-card p-4 rounded-2xl border border-white/5 flex justify-between items-center">
                    <div>
                        <div className="flex items-center space-x-2 mb-1">
                            <span className={`w-2 h-2 rounded-full ${order.status === 'DELIVERED' ? 'bg-green-500' : 'bg-red-500'}`}></span>
                            <h4 className="font-bold text-white text-sm">{order.restaurant_name}</h4>
                        </div>
                        <p className="text-[10px] text-gray-500">{new Date(order.created_at).toLocaleDateString()} • #{order.id}</p>
                    </div>
                    <div className="text-right">
                        <div className="font-black text-white">₹{order.total_amount}</div>
                        <div className="text-[9px] text-gray-500 uppercase tracking-widest">{order.status}</div>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default RiderOrders;
