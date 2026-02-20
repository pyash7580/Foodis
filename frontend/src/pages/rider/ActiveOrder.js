import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL, WS_BASE_URL } from '../../config';
import { FaChevronLeft, FaStore, FaPhone, FaLocationArrow, FaUser, FaMotorcycle } from 'react-icons/fa';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { useRider } from '../../contexts/RiderContext';
import { MapContainer, TileLayer, Marker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import useWindowSize from '../../hooks/useWindowSize';

// Fix Leaflet marker icons
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

const ActiveOrder = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { isMobile } = useWindowSize();
    const { headers, profile } = useRider();
    const [order, setOrder] = useState(null);
    const [otp, setOtp] = useState('');
    const [loading, setLoading] = useState(false);
    const [center] = useState({ lat: 23.6000, lng: 72.9500 });

    useEffect(() => {
        fetchOrderDetails();

        // 1. WebSocket for real-time status updates
        const socketUrl = `${WS_BASE_URL}/order/${id}/`;
        const ws = new WebSocket(socketUrl);

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'status_update') {
                console.log("Real-time status update received:", data.status);
                fetchOrderDetails();
            }
        };

        ws.onopen = () => console.log("Order Tracking WS Connected");
        ws.onerror = (err) => console.error("WS Error:", err);
        ws.onclose = () => console.log("Order Tracking WS Closed");

        // 2. Polling Fallback (reduced frequency to 30s)
        const interval = setInterval(fetchOrderDetails, 30000);

        return () => {
            clearInterval(interval);
            ws.close();
        };
    }, [id]);

    const fetchOrderDetails = async () => {
        try {
            const timestamp = new Date().getTime();
            const res = await axios.get(`${API_BASE_URL}/api/rider/orders/${id}/?_t=${timestamp}`, { headers });
            setOrder(res.data);
        } catch (err) {
            console.error("Failed to load order details", err);
        }
    };

    const arrivedAtRestaurant = async () => {
        try {
            await axios.post(`${API_BASE_URL}/api/rider/orders/${id}/arrived_at_restaurant/`, {}, { headers });
            toast.success("Marked as Arrived at Restaurant");
            fetchOrderDetails();
        } catch (err) { toast.error("Action failed"); }
    };

    const arrivedAtCustomer = async () => {
        try {
            await axios.post(`${API_BASE_URL}/api/rider/orders/${id}/arrived_at_customer/`, {}, { headers });
            toast.success("Marked as Arrived at Customer");
            fetchOrderDetails();
        } catch (err) { toast.error("Action failed"); }
    };

    const handlePickup = async () => {
        if (otp.length !== 6) return toast.error("Enter 6-digit Pickup OTP");
        setLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/api/rider/orders/${id}/pickup/`, { otp }, { headers });
            toast.success("Order Picked Up!");
            setOtp('');
            fetchOrderDetails();
        } catch (err) {
            const errorMsg = err.response?.data?.error || "Invalid OTP or Failed to Pickup";
            toast.error(errorMsg);
        } finally { setLoading(false); }
    };

    const handleDelivery = async () => {
        if (otp.length !== 6) return toast.error("Enter 6-digit Delivery OTP");
        setLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/api/rider/orders/${id}/deliver/`, { otp }, { headers });
            toast.success("Order Delivered Successfully!");
            navigate('/rider/dashboard');
        } catch (err) {
            const errorMsg = err.response?.data?.error || "Invalid OTP or Failed to Deliver";
            toast.error(errorMsg);
        } finally { setLoading(false); }
    };

    if (!order) return <div className="p-10 text-center text-gray-400">Loading Order...</div>;

    const isPickupPhase = ['ASSIGNED', 'ACCEPTED', 'READY', 'PREPARING', 'CONFIRMED'].includes(order.status);
    const isPickedUp = order.status === 'PICKED_UP';
    const isDeliveryPhase = order.status === 'ON_THE_WAY';

    const startDelivery = async () => {
        setLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/api/rider/orders/${order.id}/start_delivery/`, {}, { headers });
            toast.success("Delivery Started! Ride safe 🛵");
            fetchOrderDetails();
        } catch (err) {
            console.error("Start Delivery Error:", err);
            const errorMsg = err.response?.data?.error || "Action failed";
            toast.error(errorMsg);
        } finally { setLoading(false); }
    };

    const renderContent = () => (
        <div className="p-6 space-y-8 relative z-10">
            {/* 1. Restaurant Details (Pickup) */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`glass-card p-8 rounded-[2.5rem] border border-white/10 relative overflow-hidden ${!isPickupPhase && 'opacity-40 grayscale-[0.5]'}`}
            >
                {isPickupPhase && <div className="absolute top-0 right-0 w-32 h-32 bg-orange-500/10 rounded-full blur-3xl -mr-16 -mt-16 animate-pulse"></div>}

                <div className="flex items-start relative z-10">
                    <div className={`p-4 rounded-2xl mr-5 ${isPickupPhase ? 'bg-orange-500/20 text-orange-400' : 'bg-white/5 text-gray-400'}`}>
                        <FaStore className="text-2xl" />
                    </div>
                    <div className="flex-1">
                        <h3 className="font-black text-white text-xl tracking-tight mb-1">{order.restaurant_name}</h3>
                        <p className="text-gray-400 text-[11px] font-bold leading-relaxed mb-6 uppercase tracking-wider">{order.restaurant_address}</p>

                        {isPickupPhase && (
                            <div className="flex space-x-3">
                                <a href={`tel:${order.restaurant_phone}`} className="flex-1 glass-morphism py-4 rounded-2xl font-black text-[10px] uppercase tracking-widest flex items-center justify-center hover:bg-white/10 transition-all">
                                    <FaPhone className="mr-2 text-orange-400" /> Call Store
                                </a>
                                <button className="flex-1 glass-morphism py-4 rounded-2xl font-black text-[10px] uppercase tracking-widest flex items-center justify-center hover:bg-white/10 transition-all text-blue-400">
                                    <FaLocationArrow className="mr-2" /> Navigate
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {isPickupPhase && (
                    <div className="mt-10 pt-8 border-t border-white/5 relative z-10">
                        <button
                            onClick={arrivedAtRestaurant}
                            disabled={loading}
                            className={`w-full bg-[#FF3008] text-white py-5 rounded-2xl font-black text-xs uppercase tracking-[0.2em] mb-6 shadow-[0_15px_30px_rgba(255,48,8,0.3)] transition-all active:scale-95 border border-white/10 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                            {loading ? 'Confirming...' : 'Confirm Arrival'}
                        </button>

                        <div className="space-y-3">
                            <label className="block text-[9px] font-black text-gray-500 uppercase tracking-[0.3em] ml-1">Order Pickup OTP</label>
                            <div className="flex space-x-3">
                                <input
                                    type="text"
                                    value={otp}
                                    onChange={e => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                                    className="flex-1 bg-white/5 border border-white/10 rounded-2xl px-6 py-4 font-black text-center tracking-[1em] text-xl focus:border-orange-500/50 outline-none text-white placeholder:text-white/10"
                                    placeholder="••••••"
                                />
                                <button
                                    onClick={handlePickup}
                                    disabled={loading || otp.length < 6}
                                    className="bg-white text-black px-10 rounded-2xl font-black text-[10px] uppercase tracking-widest shadow-xl disabled:opacity-20 transition-all hover:bg-orange-500 hover:text-white"
                                >
                                    {loading ? '...' : 'VERIFY'}
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </motion.div>

            {/* 2. Start Delivery / Trip (Middle Step) */}
            {isPickedUp && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="glass-card p-10 rounded-[3rem] border border-blue-500/30 text-center relative overflow-hidden"
                >
                    <div className="absolute inset-0 bg-blue-600/5"></div>
                    <div className="relative z-10">
                        <div className="w-16 h-16 bg-blue-600/20 rounded-2xl mx-auto mb-6 flex items-center justify-center">
                            <FaMotorcycle className="text-blue-400 text-3xl animate-bounce" />
                        </div>
                        <h3 className="text-2xl font-black text-white mb-2">Order Picked Up!</h3>
                        <p className="text-gray-400 text-xs mb-8">Ready to start the delivery trip to {order.customer_name}?</p>
                        <button
                            onClick={startDelivery}
                            disabled={loading}
                            className="w-full bg-blue-600 text-white py-5 rounded-2xl font-black text-xs uppercase tracking-[0.2em] shadow-xl hover:bg-blue-500 active:scale-95 transition-all"
                        >
                            {loading ? 'Starting...' : 'Start Delivery Trip'}
                        </button>
                    </div>
                </motion.div>
            )}

            {/* 3. Customer Details (Drop) */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className={`glass-card p-8 rounded-[2.5rem] border border-white/10 relative overflow-hidden ${!isDeliveryPhase && 'opacity-40 grayscale-[0.5]'}`}
            >
                {isDeliveryPhase && <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl -mr-16 -mt-16 animate-pulse"></div>}

                <div className="flex items-start relative z-10">
                    <div className={`p-4 rounded-2xl mr-5 ${isDeliveryPhase ? 'bg-emerald-500/20 text-emerald-400' : 'bg-white/5 text-gray-400'}`}>
                        <FaUser className="text-2xl" />
                    </div>
                    <div className="flex-1">
                        <h3 className="font-black text-white text-xl tracking-tight mb-1">{order.customer_name}</h3>
                        <p className="text-gray-400 text-[11px] font-bold leading-relaxed mb-6 uppercase tracking-wider">{order.customer_address}</p>

                        {isDeliveryPhase && (
                            <div className="flex space-x-3">
                                <a href={`tel:${order.customer_phone}`} className="flex-1 glass-morphism py-4 rounded-2xl font-black text-[10px] uppercase tracking-widest flex items-center justify-center hover:bg-white/10 transition-all">
                                    <FaPhone className="mr-2 text-emerald-400" /> Call Client
                                </a>
                                <button className="flex-1 glass-morphism py-4 rounded-2xl font-black text-[10px] uppercase tracking-widest flex items-center justify-center hover:bg-white/10 transition-all text-blue-400">
                                    <FaLocationArrow className="mr-2" /> Live Map
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {isDeliveryPhase && (
                    <div className="mt-10 pt-8 border-t border-white/5 relative z-10">
                        <button
                            onClick={arrivedAtCustomer}
                            disabled={loading}
                            className={`w-full bg-emerald-600 text-white py-5 rounded-2xl font-black text-xs uppercase tracking-[0.2em] mb-6 shadow-[0_15px_30px_rgba(16,185,129,0.3)] transition-all active:scale-95 border border-white/10 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                            {loading ? 'Confirming...' : 'Confirm Arrival'}
                        </button>

                        <div className="space-y-3">
                            <label className="block text-[9px] font-black text-gray-500 uppercase tracking-[0.3em] ml-1">Delivery Completion OTP</label>
                            <div className="flex space-x-3">
                                <input
                                    type="text"
                                    value={otp}
                                    onChange={e => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                                    className="flex-1 bg-white/5 border border-white/10 rounded-2xl px-6 py-4 font-black text-center tracking-[1em] text-xl focus:border-emerald-500/50 outline-none text-white placeholder:text-white/10"
                                    placeholder="••••••"
                                />
                                <button
                                    onClick={handleDelivery}
                                    disabled={loading || otp.length < 6}
                                    className="bg-emerald-500 text-white px-10 rounded-2xl font-black text-[10px] uppercase tracking-widest shadow-xl disabled:opacity-20 transition-all hover:bg-emerald-400"
                                >
                                    {loading ? '...' : 'DELIVER'}
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </motion.div>

            {/* Order Items Summary */}
            <motion.div
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="glass-card p-8 rounded-[2.5rem] border border-white/5"
            >
                <h4 className="font-black text-white text-sm uppercase tracking-[0.2em] mb-6">Dispatch Manifest</h4>
                <ul className="space-y-4">
                    {order.items?.map((item, idx) => (
                        <li key={idx} className="flex justify-between items-center text-xs">
                            <div className="flex items-center space-x-3">
                                <span className="w-6 h-6 flex items-center justify-center bg-white/10 rounded-lg font-black text-[10px]">{item.quantity}</span>
                                <span className="text-gray-400 font-bold uppercase tracking-wide">{item.name}</span>
                            </div>
                            <span className="font-black text-white">₹{item.price}</span>
                        </li>
                    ))}
                </ul>
                <div className="border-t border-white/5 mt-8 pt-6 flex justify-between items-center">
                    <span className="font-black text-white uppercase text-xs tracking-widest">Total to Collect</span>
                    <span className="text-3xl font-black text-white tracking-tighter">
                        <span className="text-base font-light opacity-30 mr-1">₹</span>
                        {order.total_amount}
                    </span>
                </div>
                <div className={`mt-6 p-4 rounded-[1.2rem] text-[10px] text-center font-black uppercase tracking-widest border border-white/5 ${order.payment_method === 'COD' ? 'bg-orange-500/10 text-orange-400' : 'bg-blue-500/10 text-blue-400'}`}>
                    {order.payment_method === 'COD' ? '💰 Collect Cash on Delivery' : '💎 Digital Payment Complete'}
                </div>
            </motion.div>
        </div>
    );

    if (isMobile) {
        return (
            <div className="min-h-screen bg-[#0F172A] pb-24 font-jakarta text-white relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
                    <div className="absolute top-[-10%] left-[-10%] w-[60%] h-[40%] bg-blue-600/10 rounded-full blur-[100px]"></div>
                    <div className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[40%] bg-emerald-600/10 rounded-full blur-[100px]"></div>
                </div>

                <div className="glass-morphism-dark p-6 shadow-2xl flex items-center justify-between sticky top-0 z-[100] border-b border-white/5 mb-6">
                    <div className="flex items-center space-x-4">
                        <button onClick={() => navigate('/rider/dashboard')} className="p-3 bg-white/5 rounded-2xl border border-white/5 text-white/70">
                            <FaChevronLeft className="text-xl" />
                        </button>
                        <div>
                            <h1 className="font-black text-xl text-white tracking-tight">Active Delivery</h1>
                            <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest mt-0.5">Order #{order.id}</p>
                        </div>
                    </div>
                    <div className={`px-5 py-2 rounded-full text-[10px] font-black uppercase tracking-[0.2em] shadow-lg ${isPickupPhase ? 'bg-orange-500/20 text-orange-400 border border-orange-500/20' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/20'}`}>
                        {isPickupPhase ? 'Pickup' : 'Delivery'}
                    </div>
                </div>
                {renderContent()}
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col lg:flex-row overflow-hidden bg-[#0F172A]">
            {/* Left Panel: Details */}
            <div className="w-full lg:w-[450px] xl:w-[500px] h-full overflow-y-auto scrollbar-hide border-r border-white/5 relative z-10">
                <div className="p-8 border-b border-white/5 flex justify-between items-center bg-[#0F172A]/50 sticky top-0 z-20 backdrop-blur-md">
                    <div>
                        <h2 className="text-2xl font-black text-white tracking-tight">Active Mission</h2>
                        <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest mt-1">Order ID: #{order.id}</p>
                    </div>
                    <div className={`px-4 py-1.5 rounded-full text-[9px] font-black uppercase tracking-widest ${isPickupPhase ? 'bg-orange-500/20 text-orange-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                        {isPickupPhase ? 'Pickup' : 'Delivery'}
                    </div>
                </div>
                {renderContent()}
            </div>

            {/* Right Panel: Map */}
            <div className="flex-1 relative bg-gray-900 border-l border-white/5">
                <MapContainer
                    center={center}
                    zoom={15}
                    style={{ height: '100%', width: '100%' }}
                    zoomControl={false}
                >
                    <TileLayer
                        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    />
                    <Marker position={center} />
                </MapContainer>

                {/* Floating Status Badge */}
                <div className="absolute top-8 left-8 z-[1000] glass-morphism-dark px-6 py-4 rounded-2xl border border-white/10 shadow-2xl">
                    <div className="flex items-center space-x-4">
                        <div className={`w-3 h-3 rounded-full animate-ping ${isPickupPhase ? 'bg-orange-500' : 'bg-emerald-500'}`}></div>
                        <div>
                            <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest mb-0.5 font-bold">Live Status</p>
                            <p className="text-sm font-black text-white uppercase tracking-wider">
                                {order.status.replace('_', ' ')}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ActiveOrder;
