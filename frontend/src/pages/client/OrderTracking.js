import { API_BASE_URL } from '../../config';
import React, { useEffect, useState, useRef } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import { motion, AnimatePresence } from 'framer-motion';
import Navbar from '../../components/Navbar';
import 'leaflet/dist/leaflet.css';
import ReviewModal from '../../components/ReviewModal';
import { useAuth } from '../../contexts/AuthContext';

// Fix for default Leaflet icon markers
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

// Custom Marker Icons
const restaurantIcon = new L.Icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/3170/3170733.png',
    iconSize: [35, 35],
    iconAnchor: [17, 35],
});

const deliveryIcon = new L.Icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/2830/2830305.png',
    iconSize: [40, 40],
    iconAnchor: [20, 20],
});

const userIcon = new L.Icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/9123/9123412.png',
    iconSize: [35, 35],
    iconAnchor: [17, 17],
});

// Map View Controller to center on rider or whole route
const MapController = ({ riderPos, restaurantPos, userPos }) => {
    const map = useMap();
    useEffect(() => {
        if (riderPos) {
            map.setView([riderPos.lat, riderPos.lng], 15);
        } else if (restaurantPos && userPos) {
            const bounds = L.latLngBounds([restaurantPos.lat, restaurantPos.lng], [userPos.lat, userPos.lng]);
            map.fitBounds(bounds, { padding: [50, 50] });
        }
    }, [riderPos, restaurantPos, userPos, map]);
    return null;
};

const OrderTracking = () => {
    const { orderId } = useParams();
    const navigate = useNavigate();
    const [order, setOrder] = useState(null);
    const [loading, setLoading] = useState(true);
    const [riderLocation, setRiderLocation] = useState(null);
    const [showReviewModal, setShowReviewModal] = useState(false);
    const { token } = useAuth();
    const socketRef = useRef(null);

    const STATUS_FLOW = [
        { key: 'PENDING', label: 'Order Placed', icon: '📝', desc: 'Waiting for restaurant to confirm' },
        { key: 'CONFIRMED', label: 'Confirmed', icon: '✅', desc: 'Restaurant has accepted your order' },
        { key: 'PREPARING', label: 'Preparing', icon: '🍳', desc: 'Your food is being cooked with love' },
        { key: 'READY', label: 'Ready for Pickup', icon: '🛍️', desc: 'Order is ready and waiting for rider' },
        { key: 'ASSIGNED', label: 'Rider Assigned', icon: '🛵', desc: 'Rider is arriving at the restaurant' },
        { key: 'PICKED_UP', label: 'Picked Up', icon: '📦', desc: 'Rider has collected your order' },
        { key: 'ON_THE_WAY', label: 'On the Way', icon: '🚀', desc: 'Rider is speeding towards you!' },
        { key: 'DELIVERED', label: 'Delivered', icon: '😋', desc: 'Enjoy your meal!' }
    ];

    const getCurrentStatusIndex = (currentStatus) => {
        return STATUS_FLOW.findIndex(s => s.key === currentStatus);
    };

    useEffect(() => {
        const fetchOrderDetails = async () => {
            try {
                // Fetch order details first
                if (orderId && token) {
                    const orderRes = await axios.get(`${API_BASE_URL}/api/client/orders/${orderId}/`, {
                        headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
                    });
                    setOrder(orderRes.data);

                    // Check for review modal logic
                    const isDelivered = orderRes.data.status === 'DELIVERED';
                    const alreadyReviewed = orderRes.data.has_restaurant_review && orderRes.data.has_rider_review;

                    if (isDelivered && !alreadyReviewed) {
                        setShowReviewModal(true);
                    }

                    if (orderRes.data.rider_latitude && orderRes.data.rider_longitude) {
                        setRiderLocation({
                            lat: parseFloat(orderRes.data.rider_latitude),
                            lng: parseFloat(orderRes.data.rider_longitude)
                        });
                    }
                    setLoading(false);

                    // Connect to WebSocket with dynamic base URL
                    const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
                    const wsUrl = `${API_BASE_URL.replace(/^https?/, wsProtocol)}/ws/orders/${orderId}/?token=${token}`;
                    console.log('Connecting to WS:', wsUrl);
                    socketRef.current = new WebSocket(wsUrl);

                    socketRef.current.onmessage = (event) => {
                        const data = JSON.parse(event.data);
                        if (data.type === 'status_update') {
                            setOrder(prev => {
                                const updated = { ...prev, status: data.status };
                                // Trigger review if status changes to DELIVERED live
                                if (data.status === 'DELIVERED') {
                                    setShowReviewModal(true);
                                }
                                return updated;
                            });
                        } else if (data.type === 'location_update') {
                            setRiderLocation({
                                lat: parseFloat(data.location.latitude),
                                lng: parseFloat(data.location.longitude)
                            });
                        }
                    };
                }
                setLoading(false);
            } catch (err) {
                console.error("Error fetching order", err);
                setLoading(false);
            }
        };

        fetchOrderDetails();

        return () => {
            if (socketRef.current) socketRef.current.close();
        };
    }, [orderId, token]);

    const handleReviewSubmitted = () => {
        setShowReviewModal(false);
        // Refresh order to update review flags
        // fetchOrderDetails(); // Or just manually update state
        setOrder(prev => ({ ...prev, has_restaurant_review: true, has_rider_review: true }));
    };

    if (loading) {
        return (
            <div className="h-screen flex items-center justify-center bg-gray-50">
                <div className="w-12 h-12 border-4 border-red-600 border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    if (!order) {
        return (
            <div className="h-screen flex flex-col items-center justify-center bg-gray-50">
                <p className="text-xl font-bold text-gray-800">Order not found</p>
                <button onClick={() => navigate('/client/orders')} className="mt-4 text-red-600 font-bold">Back to Orders</button>
            </div>
        );
    }

    const currentIdx = getCurrentStatusIndex(order.status);
    const activeStatus = STATUS_FLOW[currentIdx] || STATUS_FLOW[0];

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            <Navbar />

            <ReviewModal
                isOpen={showReviewModal}
                onClose={() => setShowReviewModal(false)}
                order={order}
                onReviewSubmitted={handleReviewSubmitted}
            />

            <div className="flex-grow flex flex-col lg:flex-row">
                {/* Left Side: Status & Details */}
                <div className="lg:w-1/3 p-6 overflow-y-auto bg-white shadow-xl z-10">
                    <div className="mb-8">
                        <Link to="/client/orders" className="text-gray-400 hover:text-gray-600 flex items-center mb-4 transition">
                            <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" /></svg>
                            Back to Orders
                        </Link>
                        <h2 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-1">Order #{order.order_id}</h2>
                        <h1 className="text-2xl font-black text-gray-900">{order.restaurant?.name}</h1>
                    </div>

                    {/* Active Status Highlight */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="bg-red-50 p-6 rounded-3xl mb-8 border border-red-100"
                    >
                        <div className="flex items-center mb-3">
                            <span className="text-4xl mr-4">{activeStatus.icon}</span>
                            <div>
                                <h3 className="text-xl font-bold text-red-600">{activeStatus.label}</h3>
                                <p className="text-sm text-red-400 font-medium">{activeStatus.desc}</p>
                            </div>
                        </div>
                        {order.status !== 'DELIVERED' && (
                            <div className="mt-4 pt-4 border-t border-red-100 flex justify-between items-center">
                                <span className="text-xs font-bold text-red-400 uppercase tracking-widest">ETA: 35 MINS</span>
                                <div className="flex space-x-1">
                                    {[1, 2, 3].map(i => (
                                        <motion.div
                                            key={i}
                                            animate={{ opacity: [0.2, 1, 0.2] }}
                                            transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.3 }}
                                            className="w-1.5 h-1.5 bg-red-600 rounded-full"
                                        />
                                    ))}
                                </div>
                            </div>
                        )}
                    </motion.div>

                    {/* OTP Display for Delivery */}
                    {['PICKED_UP', 'ON_THE_WAY'].includes(order.status) && order.delivery_otp && (
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            className="bg-emerald-50 border border-emerald-100 rounded-3xl p-6 mb-8 text-center"
                        >
                            <h3 className="text-emerald-800 font-bold uppercase tracking-widest text-xs mb-2">Share this OTP with Rider</h3>
                            <div className="text-4xl font-black text-emerald-600 tracking-[0.5em]">{order.delivery_otp}</div>
                            <p className="text-xs text-emerald-500 mt-2">Only share after receiving your order completely.</p>
                        </motion.div>
                    )}

                    {/* Stepper */}
                    <div className="space-y-6 ml-4">
                        {STATUS_FLOW.map((s, idx) => {
                            const isDone = idx < currentIdx;
                            const isActive = idx === currentIdx;
                            return (
                                <div key={s.key} className="relative flex items-start">
                                    {idx !== STATUS_FLOW.length - 1 && (
                                        <div className={`absolute left-[11px] top-7 w-[2px] h-full ${isDone ? 'bg-red-600' : 'bg-gray-100'}`} />
                                    )}
                                    <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center z-10 transition-colors duration-500
                                        ${isDone ? 'bg-red-600 border-red-600' :
                                            isActive ? 'bg-white border-red-600' : 'bg-white border-gray-200'}`}
                                    >
                                        {isDone && <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" /></svg>}
                                        {isActive && <div className="w-2 h-2 bg-red-600 rounded-full animate-pulse" />}
                                    </div>
                                    <div className={`ml-4 ${isActive ? 'opacity-100' : isDone ? 'opacity-60' : 'opacity-30'}`}>
                                        <h4 className="font-bold text-sm text-gray-900">{s.label}</h4>
                                        <p className="text-xs text-gray-500">{s.desc}</p>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* Rider Info if Assigned */}
                    {order.rider && (
                        <div className="mt-10 pt-10 border-t border-gray-100">
                            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Your Delivery Partner</h3>
                            <div className="flex items-center">
                                <div className="w-14 h-14 bg-gray-100 rounded-2xl flex items-center justify-center text-3xl shadow-inner mr-4">
                                    🛵
                                </div>
                                <div className="flex-grow">
                                    <h4 className="font-bold text-gray-900">{order.rider_name || 'Rajesh Kumar'}</h4>
                                    <div className="flex items-center text-sm text-gray-500 font-medium">
                                        <span className="text-green-500 mr-1">★</span> 4.9 (500+ deliveries)
                                    </div>
                                </div>
                                <a href={`tel:${order.rider_phone || ''}`} className="w-12 h-12 bg-green-500 text-white rounded-2xl flex items-center justify-center shadow-lg hover:bg-green-600 transition">
                                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M20 15.5c-1.2 0-2.4-.2-3.6-.6-.3-.1-.7 0-1 .2l-2.2 2.2c-2.8-1.4-5.1-3.8-6.6-6.6l2.2-2.2c.3-.3.4-.7.2-1-.3-1.1-.5-2.3-.5-3.5 0-.6-.4-1-1-1H4c-.6 0-1 .4-1 1 0 9.4 7.6 17 17 17 .6 0 1-.4 1-1v-3.5c0-.6-.4-1-1-1z" /></svg>
                                </a>
                            </div>
                        </div>
                    )}
                </div>

                {/* Right Side: Map */}
                <div className="flex-grow relative h-[400px] lg:h-auto">
                    <MapContainer
                        center={[order.delivery_latitude, order.delivery_longitude]}
                        zoom={15}
                        className="w-full h-full"
                        zoomControl={false}
                    >
                        <TileLayer
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            attribution='&copy; OpenStreetMap contributors'
                        />

                        {/* Restaurant Marker */}
                        <Marker
                            position={[order.restaurant?.latitude, order.restaurant?.longitude]}
                            icon={restaurantIcon}
                        >
                            <Popup>{order.restaurant?.name}</Popup>
                        </Marker>

                        {/* User Marker */}
                        <Marker
                            position={[order.delivery_latitude, order.delivery_longitude]}
                            icon={userIcon}
                        >
                            <Popup>Your Delivery Location</Popup>
                        </Marker>

                        {/* Rider Marker */}
                        {riderLocation && (
                            <Marker
                                position={[riderLocation.lat, riderLocation.lng]}
                                icon={deliveryIcon}
                            >
                                <Popup>Rider is here</Popup>
                            </Marker>
                        )}

                        <MapController
                            riderPos={riderLocation}
                            restaurantPos={{ lat: order.restaurant?.latitude, lng: order.restaurant?.longitude }}
                            userPos={{ lat: order.delivery_latitude, lng: order.delivery_longitude }}
                        />
                    </MapContainer>

                    {/* Floating Map Actions */}
                    <div className="absolute top-6 right-6 z-[1000] flex flex-col space-y-3">
                        <button className="bg-white p-3 rounded-2xl shadow-xl text-gray-600 hover:text-red-600 transition">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default OrderTracking;
