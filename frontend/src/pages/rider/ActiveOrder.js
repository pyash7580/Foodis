import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL, WS_BASE_URL } from '../../config';
import { FaChevronLeft, FaStore, FaPhone, FaLocationArrow, FaUser, FaMotorcycle } from 'react-icons/fa';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { useRider } from '../../contexts/RiderContext';
import { MapContainer, TileLayer, Marker, Polyline, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import useWindowSize from '../../hooks/useWindowSize';

// Custom Map Icons
const createIcon = (color) => L.divIcon({
    className: 'custom-icon',
    html: `<div style="background-color: ${color}; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 15px ${color};"></div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10]
});

const riderIcon = createIcon('#3B82F6'); // Blue
const storeIcon = createIcon('#F97316'); // Orange
const userIcon = createIcon('#10B981'); // Emerald

// Component to handle auto-fitting bounds based on markers
const MapBoundsManager = ({ riderPos, storePos, userPos }) => {
    const map = useMap();
    useEffect(() => {
        const bounds = L.latLngBounds();
        let hasPoints = false;

        if (riderPos) { bounds.extend(riderPos); hasPoints = true; }
        if (storePos) { bounds.extend(storePos); hasPoints = true; }
        if (userPos) { bounds.extend(userPos); hasPoints = true; }

        if (hasPoints && bounds.isValid()) {
            map.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 });
        }
    }, [riderPos, storePos, userPos, map]);
    return null;
};

const ActiveOrder = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { isMobile } = useWindowSize();
    const { headers } = useRider();
    const [order, setOrder] = useState(null);
    const [otp, setOtp] = useState('');
    const [loading, setLoading] = useState(false);

    // Rider GPS location (mocked default, but should ideally come from rider context or navigator)
    const [riderLocation, setRiderLocation] = useState({ lat: 23.6000, lng: 72.9500 });

    const fetchOrderDetails = useCallback(async () => {
        try {
            const timestamp = new Date().getTime();
            const res = await axios.get(`${API_BASE_URL}/api/rider/orders/${id}/?_t=${timestamp}`, { headers });
            setOrder(res.data);
        } catch (err) {
            console.error("Failed to load order details", err);
        }
    }, [id, headers]);

    useEffect(() => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                pos => setRiderLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
                err => console.log(err)
            );
        }

        fetchOrderDetails();

        // WebSocket for real-time status updates
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

        // Polling Fallback
        const interval = setInterval(fetchOrderDetails, 30000);

        return () => {
            clearInterval(interval);
            ws.close();
        };
    }, [id, fetchOrderDetails]);

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

    // Calculate Map Points
    const storePos = order.restaurant_latitude && order.restaurant_longitude
        ? [parseFloat(order.restaurant_latitude), parseFloat(order.restaurant_longitude)] : null;
    const userPos = order.delivery_latitude && order.delivery_longitude
        ? [parseFloat(order.delivery_latitude), parseFloat(order.delivery_longitude)] : null;
    const riderPos = [riderLocation.lat, riderLocation.lng];

    // Determine route line color
    const routeColor = isPickupPhase ? '#F97316' : '#10B981';

    // Route logic (Rider -> Store -> User)
    const routePositions = [];
    if (isPickupPhase) {
        if (riderPos) routePositions.push(riderPos);
        if (storePos) routePositions.push(storePos);
    } else {
        if (riderPos) routePositions.push(riderPos);
        if (userPos) routePositions.push(userPos);
    }

    const MapView = () => (
        <MapContainer
            center={riderPos}
            zoom={14}
            style={{ height: '100%', width: '100%' }}
            zoomControl={false}
        >
            <TileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution='&copy; <a href="https://carto.com/">CartoDB</a>'
            />
            <MapBoundsManager riderPos={riderPos} storePos={storePos} userPos={userPos} />

            {/* Draw Path */}
            {routePositions.length > 1 && (
                <Polyline positions={routePositions} color={routeColor} weight={4} dashArray="10, 10" opacity={0.8} className="animate-pulse" />
            )}

            {/* Markers */}
            <Marker position={riderPos} icon={riderIcon} />
            {storePos && <Marker position={storePos} icon={storeIcon} />}
            {userPos && <Marker position={userPos} icon={userIcon} />}
        </MapContainer>
    );

    const renderContent = () => (
        <div className="p-4 md:p-6 space-y-6 md:space-y-8 relative z-10 w-full max-w-md mx-auto xl:max-w-full">
            {/* 1. Restaurant Details (Pickup) */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`glass-card p-6 md:p-8 rounded-[2rem] md:rounded-[2.5rem] border border-white/10 relative overflow-hidden ${!isPickupPhase && 'opacity-40 grayscale-[0.5]'}`}
            >
                {isPickupPhase && <div className="absolute top-0 right-0 w-32 h-32 bg-orange-500/10 rounded-full blur-3xl -mr-16 -mt-16 animate-pulse"></div>}

                <div className="flex items-start relative z-10">
                    <div className={`p-4 rounded-2xl mr-4 md:mr-5 ${isPickupPhase ? 'bg-orange-500/20 text-orange-400' : 'bg-white/5 text-gray-400'}`}>
                        <FaStore className="text-xl md:text-2xl" />
                    </div>
                    <div className="flex-1 w-full overflow-hidden">
                        <h3 className="font-black text-white text-lg md:text-xl tracking-tight mb-1 truncate">{order.restaurant_name}</h3>
                        <p className="text-gray-400 text-[10px] md:text-[11px] font-bold leading-relaxed mb-6 uppercase tracking-wider line-clamp-2">{order.restaurant_address}</p>

                        {isPickupPhase && (
                            <div className="flex space-x-2 md:space-x-3 w-full">
                                <a href={`tel:${order.restaurant_phone}`} className="flex-1 glass-morphism py-3 md:py-4 rounded-xl md:rounded-2xl font-black text-[9px] md:text-[10px] uppercase tracking-widest flex items-center justify-center hover:bg-white/10 transition-all truncate text-white">
                                    <FaPhone className="mr-2 text-orange-400" /> Call
                                </a>
                                <a href={`https://www.google.com/maps/dir/?api=1&destination=${order.restaurant_latitude},${order.restaurant_longitude}`} target="_blank" rel="noreferrer" className="flex-1 glass-morphism py-3 md:py-4 rounded-xl md:rounded-2xl font-black text-[9px] md:text-[10px] uppercase tracking-widest flex items-center justify-center hover:bg-white/10 transition-all text-blue-400 truncate">
                                    <FaLocationArrow className="mr-2" /> Nav
                                </a>
                            </div>
                        )}
                    </div>
                </div>

                {isPickupPhase && (
                    <div className="mt-8 md:mt-10 pt-6 md:pt-8 border-t border-white/5 relative z-10">
                        <button
                            onClick={arrivedAtRestaurant}
                            disabled={loading}
                            className={`w-full bg-[#FF3008] text-white py-4 md:py-5 rounded-2xl font-black text-[10px] md:text-xs uppercase tracking-[0.2em] mb-6 shadow-[0_15px_30px_rgba(255,48,8,0.3)] transition-all active:scale-95 border border-white/10 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                            {loading ? 'Confirming...' : 'Confirm Arrival'}
                        </button>

                        <div className="space-y-3">
                            <label className="block text-[8px] md:text-[9px] font-black text-gray-500 uppercase tracking-[0.3em] ml-1">Order Pickup OTP</label>
                            <div className="flex space-x-2 md:space-x-3">
                                <input
                                    type="text"
                                    value={otp}
                                    onChange={e => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                                    className="flex-1 w-full min-w-0 bg-white/5 border border-white/10 rounded-xl md:rounded-2xl px-4 py-3 md:py-4 font-black text-center tracking-widest md:tracking-[1em] text-lg md:text-xl focus:border-orange-500/50 outline-none text-white placeholder:text-white/10"
                                    placeholder="••••••"
                                />
                                <button
                                    onClick={handlePickup}
                                    disabled={loading || otp.length < 6}
                                    className="bg-white text-black px-6 md:px-10 rounded-xl md:rounded-2xl font-black text-[9px] md:text-[10px] uppercase tracking-widest shadow-xl disabled:opacity-20 transition-all hover:bg-orange-500 hover:text-white"
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
                    className="glass-card p-6 md:p-10 rounded-[2rem] md:rounded-[3rem] border border-blue-500/30 text-center relative overflow-hidden"
                >
                    <div className="absolute inset-0 bg-blue-600/5"></div>
                    <div className="relative z-10">
                        <div className="w-14 h-14 md:w-16 md:h-16 bg-blue-600/20 rounded-2xl mx-auto mb-4 md:mb-6 flex items-center justify-center">
                            <FaMotorcycle className="text-blue-400 text-2xl md:text-3xl animate-bounce" />
                        </div>
                        <h3 className="text-xl md:text-2xl font-black text-white mb-2">Order Picked Up!</h3>
                        <p className="text-gray-400 text-[10px] md:text-xs mb-6 md:mb-8 px-4">Ready to start the delivery trip to {order.customer_name}?</p>
                        <button
                            onClick={startDelivery}
                            disabled={loading}
                            className="w-full bg-blue-600 text-white py-4 md:py-5 rounded-2xl font-black text-[10px] md:text-xs uppercase tracking-[0.2em] shadow-xl hover:bg-blue-500 active:scale-95 transition-all"
                        >
                            {loading ? 'Starting...' : 'Start Trip'}
                        </button>
                    </div>
                </motion.div>
            )}

            {/* 3. Customer Details (Drop) */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className={`glass-card p-6 md:p-8 rounded-[2rem] md:rounded-[2.5rem] border border-white/10 relative overflow-hidden ${!isDeliveryPhase && 'opacity-40 grayscale-[0.5]'}`}
            >
                {isDeliveryPhase && <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl -mr-16 -mt-16 animate-pulse"></div>}

                <div className="flex items-start relative z-10">
                    <div className={`p-4 rounded-2xl mr-4 md:mr-5 ${isDeliveryPhase ? 'bg-emerald-500/20 text-emerald-400' : 'bg-white/5 text-gray-400'}`}>
                        <FaUser className="text-xl md:text-2xl" />
                    </div>
                    <div className="flex-1 w-full overflow-hidden">
                        <h3 className="font-black text-white text-lg md:text-xl tracking-tight mb-1 truncate">{order.customer_name}</h3>
                        <p className="text-gray-400 text-[10px] md:text-[11px] font-bold leading-relaxed mb-6 uppercase tracking-wider line-clamp-2">{order.customer_address}</p>

                        {isDeliveryPhase && (
                            <div className="flex space-x-2 md:space-x-3 w-full">
                                <a href={`tel:${order.customer_phone}`} className="flex-1 glass-morphism py-3 md:py-4 rounded-xl md:rounded-2xl font-black text-[9px] md:text-[10px] uppercase tracking-widest flex items-center justify-center hover:bg-white/10 transition-all truncate text-white">
                                    <FaPhone className="mr-2 text-emerald-400" /> Call
                                </a>
                                <a href={`https://www.google.com/maps/dir/?api=1&destination=${order.delivery_latitude},${order.delivery_longitude}`} target="_blank" rel="noreferrer" className="flex-1 glass-morphism py-3 md:py-4 rounded-xl md:rounded-2xl font-black text-[9px] md:text-[10px] uppercase tracking-widest flex items-center justify-center hover:bg-white/10 transition-all text-blue-400 truncate">
                                    <FaLocationArrow className="mr-2" /> Nav
                                </a>
                            </div>
                        )}
                    </div>
                </div>

                {isDeliveryPhase && (
                    <div className="mt-8 md:mt-10 pt-6 md:pt-8 border-t border-white/5 relative z-10">
                        <button
                            onClick={arrivedAtCustomer}
                            disabled={loading}
                            className={`w-full bg-emerald-600 text-white py-4 md:py-5 rounded-2xl font-black text-[10px] md:text-xs uppercase tracking-[0.2em] mb-6 shadow-[0_15px_30px_rgba(16,185,129,0.3)] transition-all active:scale-95 border border-white/10 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                            {loading ? 'Confirming...' : 'Confirm Arrival'}
                        </button>

                        <div className="space-y-3">
                            <label className="block text-[8px] md:text-[9px] font-black text-gray-500 uppercase tracking-[0.3em] ml-1">Delivery Completion OTP</label>
                            <div className="flex space-x-2 md:space-x-3">
                                <input
                                    type="text"
                                    value={otp}
                                    onChange={e => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                                    className="flex-1 w-full min-w-0 bg-white/5 border border-white/10 rounded-xl md:rounded-2xl px-4 py-3 md:py-4 font-black text-center tracking-widest md:tracking-[1em] text-lg md:text-xl focus:border-emerald-500/50 outline-none text-white placeholder:text-white/10"
                                    placeholder="••••••"
                                />
                                <button
                                    onClick={handleDelivery}
                                    disabled={loading || otp.length < 6}
                                    className="bg-emerald-500 text-white px-6 md:px-10 rounded-xl md:rounded-2xl font-black text-[9px] md:text-[10px] uppercase tracking-widest shadow-xl disabled:opacity-20 transition-all hover:bg-emerald-400"
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
                className="glass-card p-6 md:p-8 rounded-[2rem] md:rounded-[2.5rem] border border-white/5 mb-8"
            >
                <h4 className="font-black text-white text-[10px] md:text-sm uppercase tracking-[0.2em] mb-4 md:mb-6">Dispatch Manifest</h4>
                <ul className="space-y-3 md:space-y-4">
                    {order.items?.map((item, idx) => (
                        <li key={idx} className="flex justify-between items-start md:items-center text-[11px] md:text-xs">
                            <div className="flex items-start md:items-center space-x-2 md:space-x-3 w-2/3">
                                <span className="w-5 h-5 md:w-6 md:h-6 flex-shrink-0 flex items-center justify-center bg-white/10 rounded-lg font-black text-[9px] md:text-[10px]">{item.quantity}</span>
                                <span className="text-gray-400 font-bold uppercase tracking-wide leading-tight">{item.name}</span>
                            </div>
                            <span className="font-black text-white whitespace-nowrap">₹{item.price}</span>
                        </li>
                    ))}
                </ul>
                <div className="border-t border-white/5 mt-6 md:mt-8 pt-6 flex justify-between items-center">
                    <span className="font-black text-white uppercase text-[10px] md:text-xs tracking-widest">Total to Collect</span>
                    <span className="text-2xl md:text-3xl font-black text-white tracking-tighter">
                        <span className="text-sm md:text-base font-light opacity-30 mr-1">₹</span>
                        {order.total_amount}
                    </span>
                </div>
                <div className={`mt-6 p-4 rounded-[1.2rem] text-[9px] md:text-[10px] text-center font-black uppercase tracking-widest border border-white/5 ${order.payment_method === 'COD' ? 'bg-orange-500/10 text-orange-400' : 'bg-blue-500/10 text-blue-400'}`}>
                    {order.payment_method === 'COD' ? '💰 Collect Cash on Delivery' : '💎 Digital Payment Complete'}
                </div>
            </motion.div>
        </div>
    );

    if (isMobile) {
        return (
            <div className="h-screen w-full font-jakarta text-white relative overflow-hidden bg-gray-900">
                {/* 1. Map Background */}
                <div className="absolute inset-0 z-0 h-[60vh]">
                    <MapView />
                    <div className="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-gray-900 to-transparent z-[400] pointer-events-none"></div>
                </div>

                {/* 2. Top Header overlay */}
                <div className="absolute top-0 left-0 right-0 z-[100] p-4 pointer-events-none">
                    <div className="glass-morphism-dark p-4 rounded-3xl shadow-lg flex items-center justify-between border border-white/10 pointer-events-auto backdrop-blur-xl">
                        <button onClick={() => navigate('/rider/dashboard')} className="p-2.5 bg-white/5 hover:bg-white/10 rounded-xl transition-colors">
                            <FaChevronLeft className="text-sm text-gray-300" />
                        </button>
                        <div className="text-center">
                            <h1 className="font-black text-sm uppercase tracking-widest text-white">Active Mission</h1>
                        </div>
                        <div className={`px-3 py-1.5 rounded-full text-[8px] font-black uppercase tracking-[0.2em] shadow-lg ${isPickupPhase ? 'bg-orange-500/20 text-orange-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                            {isPickupPhase ? 'Pickup' : 'Delivery'}
                        </div>
                    </div>
                </div>

                {/* 3. Bottom Sliding Drawer Component */}
                <div className="absolute bottom-0 left-0 right-0 z-[200] h-[55vh] overflow-y-auto bg-gray-900/95 backdrop-blur-2xl rounded-t-[2.5rem] border-t border-white/10 shadow-[0_-15px_40px_rgba(0,0,0,0.5)] overscroll-contain pb-6">
                    <div className="sticky top-0 w-full flex justify-center pt-4 pb-2 bg-gradient-to-b from-gray-900/95 to-gray-900/0 z-20">
                        <div className="w-12 h-1.5 bg-white/20 rounded-full"></div>
                    </div>
                    {renderContent()}
                </div>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col lg:flex-row overflow-hidden bg-[#0F172A]">
            {/* Left Panel: Details */}
            <div className="w-full lg:w-[450px] xl:w-[500px] h-full overflow-y-auto scrollbar-hide border-r border-white/5 relative z-10 shadow-2xl">
                <div className="p-6 md:p-8 border-b border-white/5 flex justify-between items-center bg-[#0F172A]/90 sticky top-0 z-20 backdrop-blur-xl">
                    <div>
                        <h2 className="text-xl md:text-2xl font-black text-white tracking-tight">Active Mission</h2>
                        <p className="text-[9px] md:text-[10px] text-gray-500 font-black uppercase tracking-widest mt-1">Order ID: #{order.id}</p>
                    </div>
                    <div className={`px-4 py-1.5 rounded-full text-[9px] font-black uppercase tracking-widest ${isPickupPhase ? 'bg-orange-500/20 text-orange-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                        {isPickupPhase ? 'Pickup' : 'Delivery'}
                    </div>
                </div>
                {renderContent()}
            </div>

            {/* Right Panel: Map */}
            <div className="flex-1 relative bg-gray-900 z-0">
                <MapView />

                {/* Floating Status Badge */}
                <div className="absolute top-8 left-8 z-[1000] glass-morphism-dark px-6 py-4 rounded-3xl border border-white/10 shadow-2xl backdrop-blur-xl">
                    <div className="flex items-center space-x-4">
                        <div className={`w-3 h-3 rounded-full animate-ping ${isPickupPhase ? 'bg-orange-500' : 'bg-emerald-500'}`}></div>
                        <div>
                            <p className="text-[9px] md:text-[10px] text-gray-500 font-black uppercase tracking-widest mb-0.5">Live Status</p>
                            <p className="text-xs md:text-sm font-black text-white uppercase tracking-wider">
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

