import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { FaBell, FaChevronLeft, FaCheckDouble, FaTrash, FaBox, FaRupeeSign, FaInfoCircle, FaTrophy } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../../config';
import { toast } from 'react-hot-toast';

const NotificationCenter = () => {
    const navigate = useNavigate();
    const [notifications, setNotifications] = useState([]);
    const [loading, setLoading] = useState(true);

    const token = localStorage.getItem('token_rider');
    const headers = useMemo(() => ({ Authorization: `Bearer ${token}`, 'X-Role': 'RIDER' }), [token]);

    const fetchNotifications = useCallback(async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/api/rider/notifications/`, { headers });
            // Handle paginated response
            const data = res.data.results || (Array.isArray(res.data) ? res.data : []);
            setNotifications(data);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    }, [headers]);

    useEffect(() => {
        fetchNotifications();
    }, [fetchNotifications]);

    const markAllRead = async () => {
        try {
            await axios.post(`${API_BASE_URL}/api/rider/notifications/mark_all_as_read/`, {}, { headers });
            setNotifications(notifications.map(n => ({ ...n, is_read: true })));
            toast.success("All notifications marked as read");
        } catch (err) { console.error(err); }
    };

    const deleteNotification = async (id) => {
        try {
            await axios.delete(`${API_BASE_URL}/api/rider/notifications/${id}/`, { headers });
            setNotifications(notifications.filter(n => n.id !== id));
            toast.success("Notification deleted");
        } catch (err) { console.error(err); }
    };

    const getIcon = (type) => {
        switch (type) {
            case 'ORDER': return <FaBox className="text-blue-500" />;
            case 'PAYOUT': return <FaRupeeSign className="text-green-500" />;
            case 'INCENTIVE': return <FaTrophy className="text-yellow-500" />;
            default: return <FaInfoCircle className="text-gray-500" />;
        }
    };

    const getBgColor = (type) => {
        switch (type) {
            case 'ORDER': return 'bg-blue-50';
            case 'PAYOUT': return 'bg-green-50';
            case 'INCENTIVE': return 'bg-yellow-50';
            default: return 'bg-gray-50';
        }
    };

    return (
        <div className="min-h-screen bg-white font-jakarta">
            {/* Header */}
            <div className="bg-white p-4 sticky top-0 z-50 border-b flex justify-between items-center">
                <div className="flex items-center">
                    <button onClick={() => navigate(-1)} className="p-2 -ml-2">
                        <FaChevronLeft className="text-gray-600" />
                    </button>
                    <h1 className="text-xl font-black ml-2">Notifications</h1>
                </div>
                <button onClick={markAllRead} className="p-2 text-blue-600">
                    <FaCheckDouble />
                </button>
            </div>

            <div className="p-0">
                {loading ? (
                    <div className="flex justify-center items-center h-64">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600"></div>
                    </div>
                ) : (
                    <div className="divide-y">
                        {notifications.length === 0 ? (
                            <div className="p-12 text-center">
                                <FaBell className="text-5xl text-gray-100 mx-auto mb-4" />
                                <p className="text-gray-400 font-bold">No notifications yet</p>
                            </div>
                        ) : (
                            <AnimatePresence>
                                {notifications.map((n) => (
                                    <motion.div
                                        key={n.id}
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        exit={{ opacity: 0, x: -100 }}
                                        className={`p-5 flex items-start space-x-4 ${!n.is_read ? 'bg-blue-50/30' : ''}`}
                                    >
                                        <div className={`p-3 rounded-2xl ${getBgColor(n.notification_type)}`}>
                                            {getIcon(n.notification_type)}
                                        </div>
                                        <div className="flex-1">
                                            <div className="flex justify-between items-start">
                                                <h3 className={`font-black text-sm ${!n.is_read ? 'text-gray-900' : 'text-gray-600'}`}>{n.title}</h3>
                                                <button onClick={() => deleteNotification(n.id)} className="text-gray-300 hover:text-red-500">
                                                    <FaTrash className="text-xs" />
                                                </button>
                                            </div>
                                            <p className="text-xs text-gray-500 mt-1 font-medium leading-relaxed">{n.message}</p>
                                            <p className="text-[10px] text-gray-400 mt-2 font-bold uppercase tracking-wider">
                                                {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </p>
                                        </div>
                                    </motion.div>
                                ))}
                            </AnimatePresence>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default NotificationCenter;
