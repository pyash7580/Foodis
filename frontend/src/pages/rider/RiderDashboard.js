import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { motion, AnimatePresence } from 'framer-motion';
import { FaMotorcycle, FaMapMarkerAlt, FaPowerOff, FaSync, FaBox, FaRupeeSign, FaStar, FaHome, FaClipboardList, FaWallet, FaUser, FaBell, FaTrophy, FaChevronRight } from 'react-icons/fa';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { API_BASE_URL, WS_BASE_URL } from '../../config';
import { useNavigate } from 'react-router-dom';
import OrderRequestModal from './OrderRequestModal';
import { toast } from 'react-hot-toast';
import { useAuth } from '../../contexts/AuthContext';
import { useRider } from '../../contexts/RiderContext';

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

const RiderDashboard = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const { profile, isOnline, activeOrder, stats: riderStats, toggleOnline, fetchRiderData: refreshContext } = useRider();
    const [newOrder, setNewOrder] = useState(null); // Incoming request
    const [location, setLocation] = useState({ lat: 23.6000, lng: 72.9500 }); // Default Himmatnagar
    const [lastLocUpdate, setLastLocUpdate] = useState(Date.now());
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [incentiveProgress, setIncentiveProgress] = useState([]);

    // WebSocket
    const ws = useRef(null);
    const watchId = useRef(null);

    const token = localStorage.getItem('token_rider');
    const headers = { Authorization: `Bearer ${token}`, 'X-Role': 'RIDER' };

    // 1. Initial Data Fetch
    useEffect(() => {
        fetchDashboardData();
    }, []);

    // 2. WebSocket Connection (For Order Alerts)
    useEffect(() => {
        if (!process.env.REACT_APP_WS_URL && !window.location.origin) return;

        // Determine WS URL (handling http/https)
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // Use config WS_BASE_URL or fallback
        const wsUrl = WS_BASE_URL || `${wsProtocol}//${window.location.hostname}:8000/ws`;

        if (user && user.id) {
            const socketUrl = `${wsUrl}/notifications/${user.id}/`;
            console.log("Connecting to WS:", socketUrl);

            ws.current = new WebSocket(socketUrl);

            ws.current.onopen = () => console.log("WS Connected");
            ws.current.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log("WS Message:", data);
                if (data.message && data.message.type === 'order_assigned') {
                    toast.success("New Order Assigned!", { icon: '🔔' });
                    fetchDashboardData(); // Refresh to get active order
                }
                // Handle 'order_request' if we implemented a bidding system
            };
            ws.current.onclose = () => console.log("WS Disconnected");

            return () => {
                if (ws.current) ws.current.close();
            };
        }
    }, [user]);

    // 3. Location Tracking (Only when Online)
    useEffect(() => {
        if (isOnline) {
            if (navigator.geolocation) {
                // watchPosition for continuous tracking
                watchId.current = navigator.geolocation.watchPosition(
                    (pos) => {
                        const { latitude, longitude } = pos.coords;
                        setLocation({ lat: latitude, lng: longitude });

                        // Throttle backend updates (e.g., once every 10 seconds)
                        const now = Date.now();
                        if (now - lastLocUpdate > 10000) {
                            updateLocationBackend(latitude, longitude);
                            setLastLocUpdate(now);
                        }
                    },
                    (err) => console.error("Geo Error", err),
                    { enableHighAccuracy: true, maximumAge: 0 }
                );
            }
        } else {
            if (watchId.current) navigator.geolocation.clearWatch(watchId.current);
        }

        return () => {
            if (watchId.current) navigator.geolocation.clearWatch(watchId.current);
        };
    }, [isOnline, lastLocUpdate]);

    // 4. Polling Fallback (For reliable order fetching if WS fails or for pool)
    useEffect(() => {
        const interval = setInterval(() => {
            if (isOnline && !activeOrder) {
                checkForOrders();
            }
        }, 10000); // 10s polling

        return () => clearInterval(interval);
    }, [isOnline, activeOrder]);

    const updateLocationBackend = async (lat, lng) => {
        if (!profile) return;
        try {
            await axios.post(`${API_BASE_URL}/api/rider/profile/${profile.id}/update_location/`, {
                latitude: lat,
                longitude: lng
            }, { headers });
            console.log("Location Synced 📍");
        } catch (err) { console.error("Loc update failed", err); }
    };

    const fetchDashboardData = async () => {
        try {
            await refreshContext();
            // Fetch extra data
            fetchNotifications();
            fetchIncentives();
        } catch (err) {
            if (err.response && err.response.status === 401) navigate('/rider/login');
            console.error(err);
        }
    };

    const fetchNotifications = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/api/rider/notifications/`, { headers });
            setNotifications(res.data);
            setUnreadCount(res.data.filter(n => !n.is_read).length);
        } catch (err) { console.error(err); }
    };

    const fetchIncentives = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/api/rider/incentives/progress/`, { headers });
            setIncentiveProgress(res.data);
        } catch (err) { console.error(err); }
    };


    const checkForOrders = async () => {
        try {
            const timestamp = new Date().getTime();
            const res = await axios.get(`${API_BASE_URL}/api/rider/orders/available/?_t=${timestamp}`, { headers });
            if (res.data && res.data.length > 0) {
                const nearest = res.data[0];
                const orderData = nearest.order ? nearest.order : nearest;
                const dist = nearest.distance || 0;
                setNewOrder({ ...orderData, distance: dist });
            }
        } catch (err) { }
    };

    const handleAcceptOrder = async (orderId) => {
        try {
            const res = await axios.post(`${API_BASE_URL}/api/rider/orders/${orderId}/accept/`, {}, { headers });
            setActiveOrder(res.data);
            setNewOrder(null);
            toast.success("Order Accepted!");
            navigate(`/rider/order/${orderId}`);
        } catch (err) {
            toast.error("Failed to accept order. It might be taken.");
            setNewOrder(null);
        }
    };

    const handleRejectOrder = () => {
        setNewOrder(null);
    };

    return (
        <div className="h-screen w-full relative bg-[#0F172A] text-white font-jakarta overflow-hidden">
            {/* Background Decorative Blobs */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
                <div className="absolute top-[10%] left-[-10%] w-[60%] h-[40%] bg-red-600/10 rounded-full blur-[100px]"></div>
                <div className="absolute bottom-[20%] right-[-10%] w-[60%] h-[40%] bg-blue-600/10 rounded-full blur-[100px]"></div>
            </div>

            {/* 1. Header Overlay */}
            <div className="absolute top-6 left-6 right-6 z-[999] flex justify-between items-start pointer-events-none">
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="glass-morphism-dark p-4 rounded-3xl shadow-2xl pointer-events-auto flex items-center space-x-4 border border-white/5"
                >
                    <div className="bg-gradient-to-br from-[#FF3008] to-[#FF6B00] p-3 rounded-2xl shadow-lg ring-4 ring-red-500/10">
                        <FaMotorcycle className="text-white text-xl" />
                    </div>
                    <div>
                        <p className="text-[8px] text-gray-400 font-black uppercase tracking-[0.2em]">Active Zone</p>
                        <p className="text-sm font-black text-white flex items-center">
                            {profile?.city || 'Locating...'}
                            {isOnline && <div className="ml-2 w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_#10B981]" />}
                        </p>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="pointer-events-auto flex items-center space-x-3"
                >
                    <button
                        onClick={() => navigate('/rider/notifications')}
                        className="glass-morphism-dark p-4 rounded-3xl shadow-xl relative border border-white/5"
                    >
                        <FaBell className="text-gray-400 text-xl" />
                        {unreadCount > 0 && (
                            <span className="absolute top-3 right-3 w-3 h-3 bg-red-500 border-2 border-[#0F172A] rounded-full shadow-[0_0_10px_rgba(239,68,68,0.5)]"></span>
                        )}
                    </button>

                    <button
                        onClick={toggleOnline}
                        className={`flex flex-col items-center justify-center p-4 rounded-3xl shadow-2xl transition-all duration-500 transform active:scale-95 border border-white/5 w-24 ${isOnline
                            ? 'bg-gradient-to-br from-emerald-500 to-teal-600 text-white shadow-[0_10px_20px_rgba(16,185,129,0.3)]'
                            : 'glass-morphism-dark text-gray-500'
                            }`}
                    >
                        <FaPowerOff className={`text-xl mb-1 ${isOnline ? 'animate-pulse' : ''}`} />
                        <span className="text-[8px] font-black uppercase tracking-wider">{isOnline ? 'Active' : 'Offline'}</span>
                    </button>
                </motion.div>
            </div>


            {/* 1.5. Stat Cards Grid / Current Mission Overlay */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="absolute top-28 left-6 right-6 z-[998] pointer-events-none"
            >
                {activeOrder ? (
                    <div className="glass-morphism-dark p-6 rounded-[2.5rem] border border-orange-500/30 shadow-2xl pointer-events-auto relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-orange-500/10 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-orange-500/20 transition-all"></div>

                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center space-x-3">
                                <div className="p-2 bg-orange-500/20 rounded-xl">
                                    <FaMotorcycle className="text-orange-500 text-xl animate-bounce" />
                                </div>
                                <div>
                                    <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest">Ongoing Mission</p>
                                    <h3 className="text-lg font-black text-white">{activeOrder.restaurant_name}</h3>
                                </div>
                            </div>
                            <button
                                onClick={() => navigate(`/rider/order/${activeOrder.id}`)}
                                className="p-3 bg-white/5 rounded-2xl hover:bg-white/10 transition-colors"
                            >
                                <FaChevronRight className="text-gray-400" />
                            </button>
                        </div>

                        <div className="flex items-center space-x-3">
                            <div className="flex-1 bg-white/5 h-1.5 rounded-full overflow-hidden">
                                <motion.div
                                    className="h-full bg-orange-500"
                                    initial={{ width: '20%' }}
                                    animate={{ width: activeOrder.status === 'ON_THE_WAY' ? '80%' : '40%' }}
                                />
                            </div>
                            <span className="text-[10px] font-black text-orange-400 uppercase tracking-widest">
                                {activeOrder.status.replace('_', ' ')}
                            </span>
                        </div>
                    </div>
                ) : (
                    <div className="grid grid-cols-4 gap-3">
                        {/* Stat 1 */}
                        <div className="glass-morphism-dark p-3 rounded-2xl border border-white/5 text-center backdrop-blur-xl">
                            <p className="text-[18px] font-black text-white">{riderStats?.today_deliveries || 0}</p>
                            <p className="text-[7px] text-gray-500 font-black uppercase tracking-widest mt-0.5">Orders</p>
                        </div>
                        {/* Stat 2 */}
                        <div className="glass-morphism-dark p-3 rounded-2xl border border-white/5 text-center backdrop-blur-xl">
                            <p className="text-[18px] font-black text-[#10B981]">₹{Math.round(riderStats?.today_earnings || 0)}</p>
                            <p className="text-[7px] text-gray-500 font-black uppercase tracking-widest mt-0.5">Earnings</p>
                        </div>
                        {/* Stat 3 */}
                        <div className="glass-morphism-dark p-3 rounded-2xl border border-white/5 text-center backdrop-blur-xl">
                            <p className="text-[18px] font-black text-[#FF3008]">₹{Math.round(riderStats?.wallet_balance || 0)}</p>
                            <p className="text-[7px] text-gray-500 font-black uppercase tracking-widest mt-0.5">Wallet</p>
                        </div>
                        {/* Stat 4 */}
                        <div className="glass-morphism-dark p-3 rounded-2xl border border-white/5 text-center backdrop-blur-xl">
                            <p className="text-[18px] font-black text-orange-400">{riderStats?.rating?.toFixed(1) || '0.0'}</p>
                            <p className="text-[7px] text-gray-500 font-black uppercase tracking-widest mt-0.5">Rating</p>
                        </div>
                    </div>
                )}
            </motion.div>


            {/* 2. Map Layer */}
            <div className="absolute inset-0 z-0">
                <MapContainer center={[location.lat, location.lng]} zoom={15} style={{ height: '100%', width: '100%' }} zoomControl={false}>
                    <TileLayer
                        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                        attribution='&copy; <a href="https://carto.com/">CartoDB</a>'
                    />
                    <MapController center={[location.lat, location.lng]} />
                    <Marker position={[location.lat, location.lng]}>
                        <Popup>Rider Current Position</Popup>
                    </Marker>
                </MapContainer>

                {/* 2.5. Floating Target Progress */}
                {isOnline && incentiveProgress.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, x: -100 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="absolute bottom-64 left-6 z-[998] glass-morphism-dark p-4 rounded-3xl shadow-2xl border border-white/5 max-w-[200px]"
                        onClick={() => navigate('/rider/incentives')}
                    >
                        <div className="flex items-center space-x-3 mb-3">
                            <div className="p-1.5 bg-yellow-500/10 rounded-lg">
                                <FaTrophy className="text-yellow-500 text-sm" />
                            </div>
                            <span className="text-[9px] font-black text-gray-300 uppercase tracking-widest">Target Progress</span>
                        </div>
                        {incentiveProgress.map(p => (
                            <div key={p.id}>
                                <div className="flex justify-between text-[10px] font-black text-white mb-2">
                                    <span>{p.current_count}/{p.scheme_details.target_count} Trips</span>
                                    <span className="text-emerald-400">₹{p.scheme_details.reward_amount}</span>
                                </div>
                                <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                                    <motion.div
                                        className="h-full bg-gradient-to-r from-yellow-400 to-orange-500 shadow-[0_0_10px_rgba(245,158,11,0.5)]"
                                        initial={{ width: 0 }}
                                        animate={{ width: `${(p.current_count / p.scheme_details.target_count) * 100}%` }}
                                        transition={{ duration: 1 }}
                                    />
                                </div>
                            </div>
                        )).slice(0, 1)}
                    </motion.div>
                )}
            </div>


            {/* 3. Bottom Status Card / Active Order Card */}
            <AnimatePresence>
                {!newOrder && (
                    <motion.div
                        initial={{ y: 100, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        exit={{ y: 100, opacity: 0 }}
                        className="absolute bottom-24 left-6 right-6 z-[999]"
                    >
                        {!isOnline ? (
                            <div className="glass-morphism-dark p-8 rounded-[2.5rem] shadow-[0_20px_50px_rgba(0,0,0,0.5)] text-center border border-white/5">
                                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center mx-auto mb-6 shadow-inner border border-white/5">
                                    <FaPowerOff className="text-3xl text-gray-600" />
                                </div>
                                <h3 className="text-2xl font-black mb-2 text-white">System Offline</h3>
                                <p className="text-gray-500 text-sm mb-8 font-bold">Go online to receive high-priority delivery requests in your zone.</p>
                                <button
                                    onClick={toggleOnline}
                                    className="w-full bg-gradient-to-r from-emerald-500 to-teal-600 text-white py-5 rounded-2xl font-black text-lg shadow-[0_15px_30px_rgba(16,185,129,0.3)] active:scale-95 transition-all"
                                >
                                    GO ONLINE
                                </button>
                            </div>
                        ) : activeOrder ? (
                            <div
                                onClick={() => navigate(`/rider/order/${activeOrder.id}`)}
                                className="glass-morphism-dark p-6 rounded-[2.5rem] shadow-2xl border-t-2 border-orange-500/50 flex items-center justify-between cursor-pointer"
                            >
                                <div className="flex items-center space-x-4">
                                    <div className="bg-orange-500/20 p-4 rounded-2xl">
                                        <FaMotorcycle className="text-orange-500 text-2xl animate-pulse" />
                                    </div>
                                    <div>
                                        <h3 className="font-black text-white text-lg leading-tight">{activeOrder.restaurant_name}</h3>
                                        <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">{activeOrder.status.replace('_', ' ')}</p>
                                    </div>
                                </div>
                                <div className="bg-white/5 p-3 rounded-2xl">
                                    <FaChevronRight className="text-gray-500" />
                                </div>
                            </div>
                        ) : (
                            <div className="glass-morphism-dark p-6 rounded-[2.5rem] shadow-2xl border-t-2 border-emerald-500/50">
                                <div className="flex items-center justify-center space-x-4 mb-4">
                                    <div className="relative flex h-3 w-3">
                                        <div className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></div>
                                        <div className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></div>
                                    </div>
                                    <h3 className="font-black text-white text-lg tracking-tight uppercase tracking-widest">Searching Zone...</h3>
                                </div>
                                <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                                    <motion.div
                                        className="h-full bg-gradient-to-r from-emerald-400 to-teal-500 shadow-[0_0_10px_#10B981]"
                                        animate={{ x: ["-100%", "100%"] }}
                                        transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                                    />
                                </div>
                            </div>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>

            {/* 4. Order Request Modal */}
            <OrderRequestModal
                order={newOrder}
                onAccept={handleAcceptOrder}
                onReject={handleRejectOrder}
            />

            {/* 5. Mobile Bottom Nav Overlay (managed by Layout, but shadowed here for visual consistency if needed) */}
            {/* Note: RiderLayout handles the actual nav, keeping background consistent */}
        </div>
    );
};

// Helper component to center map smoothly
const MapController = ({ center }) => {
    const map = useMap();
    useEffect(() => {
        map.flyTo(center, map.getZoom());
    }, [center, map]);
    return null;
};

export default RiderDashboard;
