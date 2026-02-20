import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../config';

const RiderStatus = () => {
    const [status, setStatus] = useState('Checking...');

    useEffect(() => {
        const token = localStorage.getItem('token_rider');
        axios.get(`${API_BASE_URL}/api/rider/profile/`, { headers: { Authorization: `Bearer ${token}`, 'X-Role': 'RIDER' } })
            .then(res => {
                const data = res.data.results || (Array.isArray(res.data) ? res.data : []);
                if (data.length > 0) setStatus(data[0].status);
            })
            .catch(() => setStatus('Error'));
    }, []);

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-6 text-center">
            <h1 className="text-3xl font-black text-gray-900 mb-4">Application Status</h1>
            <div className="bg-white p-8 rounded-3xl shadow-lg w-full max-w-sm">
                <p className="text-gray-500 mb-2 font-bold uppercase text-xs">Current Status</p>
                <p className="text-2xl font-black text-red-600 mb-6">{status}</p>

                {status === 'UNDER_REVIEW' && (
                    <p className="text-gray-600">Your application is under review by our admin team. This usually takes 24-48 hours. You will be notified once approved.</p>
                )}

                {status === 'REJECTED' && (
                    <p className="text-red-600">Unfortunately, your application was not approved. Please contact support.</p>
                )}
            </div>
        </div>
    );
};

export default RiderStatus;
