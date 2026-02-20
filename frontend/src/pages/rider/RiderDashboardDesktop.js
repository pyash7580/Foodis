import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { motion } from 'framer-motion';
import { FaMotorcycle, FaBox, FaRupeeSign, FaStar, FaMapMarkerAlt, FaWallet, FaPowerOff } from 'react-icons/fa';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { API_BASE_URL, WS_BASE_URL } from '../../config';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { useAuth } from '../../contexts/AuthContext';
import { useRider } from '../../contexts/RiderContext';
import OrderRequestModal from './OrderRequestModal';
import DashboardStatCard from '../../components/rider/DashboardStatCard';

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

const RiderDashboardDesktop = () => {
    const navigate = useNavigate();
    const { profile, isOnline, stats } = useRider();
    const [location, setLocation] = useState({ lat: 23.6000, lng: 72.9500 });
    const [lastLocUpdate, setLastLocUpdate] = useState(Date.now());
    const watchId = useRef(null);

    // 1. Location Tracking (Only when Online)
    useEffect(() => {
        if (isOnline && navigator.geolocation) {
            watchId.current = navigator.geolocation.watchPosition(
                (pos) => {
                    const { latitude, longitude } = pos.coords;
                    setLocation({ lat: latitude, lng: longitude });
                    const now = Date.now();
                    if (now - lastLocUpdate > 10000) {
                        updateLocationBackend(latitude, longitude);
                        setLastLocUpdate(now);
                    }
                },
                (err) => console.error("Geo Error", err),
                { enableHighAccuracy: true, maximumAge: 0 }
            );
        } else {
            if (watchId.current) navigator.geolocation.clearWatch(watchId.current);
        }
        return () => { if (watchId.current) navigator.geolocation.clearWatch(watchId.current); };
    }, [isOnline, lastLocUpdate]);

    const updateLocationBackend = async (lat, lng) => {
        if (!profile) return;
        try {
            await axios.post(`${API_BASE_URL}/api/rider/profile/${profile.id}/update_location/`, {
                latitude: lat, longitude: lng
            }, { headers: { Authorization: `Bearer ${localStorage.getItem('token_rider')}`, 'X-Role': 'RIDER' } });
        } catch (err) { console.error("Loc update failed", err); }
    };

    return (
        <div className="flex flex-col space-y-8 animate-in fade-in duration-500">
            {/* 1. Header Row: Metrics Grid */}
            <div className="grid grid-cols-4 gap-6">
                <DashboardStatCard
                    title="Total Orders"
                    value={stats.today_deliveries}
                    icon={FaBox}
                    color="blue"
                    trend="+12% Today"
                    index={0}
                />
                <DashboardStatCard
                    title="Today's Earnings"
                    value={`₹${stats.today_earnings}`}
                    icon={FaRupeeSign}
                    color="emerald"
                    trend="Live Sync"
                    index={1}
                />
                <DashboardStatCard
                    title="Wallet Balance"
                    value={`₹${stats.wallet_balance}`}
                    icon={FaWallet}
                    color="purple"
                    trend="Withdraw"
                    index={2}
                />
                <DashboardStatCard
                    title="Rider Rating"
                    value={stats.rating?.toFixed(1) || '0.0'}
                    icon={FaStar}
                    color="orange"
                    trend="Excellent"
                    index={3}
                />
            </div>

            {/* 2. Content Row: Map + Insights */}
            <div className="grid grid-cols-3 gap-8 min-h-[500px]">
                {/* Large Map Section (2/3) */}
                <div className="col-span-2 glass-morphism-dark rounded-[2.5rem] border border-white/5 overflow-hidden relative shadow-2xl">
                    <MapContainer center={[location.lat, location.lng]} zoom={15} style={{ height: '100%', width: '100%' }} zoomControl={false}>
                        <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />
                        <Marker position={[location.lat, location.lng]} />
                    </MapContainer>

                    {/* Map Overlays */}
                    <div className="absolute top-6 left-6 z-[1000]">
                        <div className="bg-[#111827]/80 backdrop-blur-xl p-4 rounded-2xl border border-white/5 shadow-2xl">
                            <p className="text-[8px] font-black text-gray-500 uppercase tracking-widest mb-1">Live Zone</p>
                            <div className="flex items-center space-x-2">
                                <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></div>
                                <span className="text-sm font-black text-white">{profile?.city || 'Himmatnagar'}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Performance & Status Panel (1/3) */}
                <div className="col-span-1 space-y-6">
                    <div className="glass-morphism-dark rounded-[2.5rem] border border-white/5 p-8 h-full flex flex-col shadow-2xl overflow-hidden">
                        <div className="flex items-center justify-between mb-8">
                            <h3 className="text-xl font-black text-white tracking-tight">Status Overview</h3>
                            <div className={`px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest ${isOnline ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                                {isOnline ? 'Active' : 'Offline'}
                            </div>
                        </div>

                        <div className="flex-1 flex flex-col items-center justify-center text-center space-y-6">
                            <div className={`w-24 h-24 rounded-full border border-white/5 flex items-center justify-center shadow-2xl ${isOnline ? 'bg-emerald-500/10 text-emerald-500 shadow-emerald-500/10' : 'bg-gray-900 text-gray-700'}`}>
                                <FaMotorcycle className={`text-4xl ${isOnline ? 'animate-bounce' : ''}`} />
                            </div>

                            <div>
                                <h4 className="text-xl font-black text-white">{isOnline ? 'Ready for Mission' : 'System Standby'}</h4>
                                <p className="text-sm text-gray-500 mt-2 font-medium px-4">
                                    {isOnline
                                        ? "You are currently online and visible in the delivery zone. New orders will appear in the Orders section."
                                        : "You are currently offline. Toggle your status in the sidebar to start receiving delivery requests."
                                    }
                                </p>
                            </div>

                            <button
                                onClick={() => navigate('/rider/orders')}
                                className="w-full bg-white/5 hover:bg-white/10 border border-white/5 text-white py-4 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] transition-all"
                            >
                                GO TO ORDERS
                            </button>
                        </div>

                        {/* Quick Stats Bottom */}
                        <div className="pt-8 border-t border-white/5 mt-auto">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <p className="text-[8px] font-black text-gray-500 uppercase tracking-widest mb-1">Today's Goal</p>
                                    <p className="text-sm font-black text-white">{stats.today_deliveries} / 15</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-[8px] font-black text-gray-500 uppercase tracking-widest mb-1">Top Speed</p>
                                    <p className="text-sm font-black text-white">42 km/h</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RiderDashboardDesktop;
