import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { API_BASE_URL, WS_BASE_URL } from '../config';
import { toast } from 'react-hot-toast';

const RiderContext = createContext();

export const useRider = () => useContext(RiderContext);

export const RiderProvider = ({ children }) => {
    const [profile, setProfile] = useState(null);
    const [isOnline, setIsOnline] = useState(false);
    const [activeOrder, setActiveOrder] = useState(null);
    const [stats, setStats] = useState({
        today_deliveries: 0,
        today_earnings: '0.00',
        rating: 0.0,
        total_deliveries: 0,
        wallet_balance: '0.00'
    });
    const [loading, setLoading] = useState(true);
    const token = localStorage.getItem('token_rider');
    const headers = {
        Authorization: `Bearer ${token}`,
        'X-Role': 'RIDER'
    };
    const ws = useRef(null);

    const fetchRiderData = async () => {
        const currentToken = localStorage.getItem('token_rider');
        if (!currentToken) return;

        try {
            const timestamp = new Date().getTime();
            const config = {
                headers: {
                    Authorization: `Bearer ${currentToken}`,
                    'X-Role': 'RIDER'
                }
            };
            const res = await axios.get(`${API_BASE_URL}/api/rider/profile/dashboard/?_t=${timestamp}`, config);
            if (res.data) {
                const { profile: p, stats: s, active_order } = res.data;
                setProfile(p);
                setIsOnline(p.is_online);
                setActiveOrder(active_order || null);
                setStats({
                    today_deliveries: s.today_deliveries || 0,
                    today_earnings: s.today_earnings || '0.00',
                    rating: p.rating || 0.0,
                    total_deliveries: p.total_deliveries || 0,
                    wallet_balance: p.wallet_balance || '0.00'
                });
            }
        } catch (err) {
            console.error("Failed to fetch rider data", err);
        } finally {
            setLoading(false);
        }
    };

    const toggleOnline = async () => {
        if (!profile) return;
        try {
            const res = await axios.post(`${API_BASE_URL}/api/rider/profile/${profile.id}/toggle_online/`, {}, { headers });
            setIsOnline(res.data.is_online);
            toast.success(res.data.is_online ? "You are now ONLINE" : "You are now OFFLINE");
            fetchRiderData(); // Refresh state
        } catch (err) {
            toast.error("Failed to toggle status");
        }
    };

    useEffect(() => {
        fetchRiderData();
    }, [token]);

    return (
        <RiderContext.Provider value={{
            profile,
            isOnline,
            stats,
            activeOrder,
            setActiveOrder,
            loading,
            toggleOnline,
            fetchRiderData,
            headers
        }}>
            {children}
        </RiderContext.Provider>
    );
};
