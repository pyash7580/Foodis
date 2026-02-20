import { API_BASE_URL } from '../../config';

import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import toast from 'react-hot-toast';

const RestaurantSignup = () => {
    const [step, setStep] = useState(1); // 1: User Auth, 2: Restaurant Details
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // User Auth States
    const [mobile, setMobile] = useState('');
    const [email, setEmail] = useState('');
    const [name, setName] = useState('');
    const [otp, setOtp] = useState('');
    const [otpSent, setOtpSent] = useState(false);

    // Restaurant Details States
    const [restaurantData, setRestaurantData] = useState({
        name: '',
        cuisine: '',
        phone: '',
        email: '',
        address: '',
        city: '',
        state: '',
        pincode: '',
        gst_number: '',
        pan_number: '',
        fssai_license: '',
        latitude: 12.9716, // Default Bangalore
        longitude: 77.5946
    });

    const { sendOtp, verifyOtp } = useAuth();
    const navigate = useNavigate();

    const handleSendOtp = async (e) => {
        e.preventDefault();
        setLoading(true);
        const res = await sendOtp(mobile, 'mobile');
        if (res.success) {
            setOtpSent(true);
            toast.success("OTP sent to your mobile");
            if (res.otp) {
                toast.custom((t) => (
                    <div className="bg-white shadow-lg rounded-lg p-4 border-l-4 border-red-500">
                        <p className="font-bold">Test OTP: {res.otp}</p>
                    </div>
                ));
            }
        } else {
            setError(res.error);
        }
        setLoading(false);
    };

    const handleVerifyOtp = async (e) => {
        e.preventDefault();
        setLoading(true);
        const res = await verifyOtp(mobile, otp, 'mobile', name, 'RESTAURANT');
        if (res.success) {
            setStep(2);
            toast.success("Account created! Now tell us about your restaurant.");
        } else {
            setError(res.error);
        }
        setLoading(false);
    };

    const handleRestaurantSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            // 1. Create Restaurant
            const res = await axios.post(`${API_BASE_URL}/api/restaurant/restaurant/`, {
                name: restaurantData.name,
                cuisine: restaurantData.cuisine,
                phone: restaurantData.phone || mobile,
                email: restaurantData.email || email,
                address: restaurantData.address,
                city: restaurantData.city,
                state: restaurantData.state,
                pincode: restaurantData.pincode,
                latitude: restaurantData.latitude,
                longitude: restaurantData.longitude,
                slug: restaurantData.name.toLowerCase().replace(/ /g, '-') + '-' + Date.now()
            });

            const restaurantId = res.data.id;

            // 2. Update Profile with Documents
            await axios.put(`${API_BASE_URL}/api/restaurant/restaurant/${restaurantId}/profile/`, {
                gst_number: restaurantData.gst_number,
                pan_number: restaurantData.pan_number,
                fssai_license: restaurantData.fssai_license
            });

            toast.success("Restaurant registered successfully! Pending approval.");
            navigate('/restaurant/pending');
        } catch (err) {
            console.error(err);
            let errMsg = "Failed to register restaurant. Check all fields.";
            if (err.response && err.response.data) {
                if (typeof err.response.data === 'object') {
                    const fields = Object.keys(err.response.data);
                    const messages = Object.values(err.response.data).flat();
                    errMsg = `${fields[0].toUpperCase()}: ${messages[0]}`;
                } else if (typeof err.response.data === 'string') {
                    errMsg = err.response.data;
                }
            }
            toast.error(errMsg);
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setRestaurantData({ ...restaurantData, [e.target.name]: e.target.value });
    };

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto">
                <div className="text-center mb-10">
                    <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Partner with Foodis</h1>
                    <p className="mt-4 text-lg text-gray-600">Register your restaurant and start growing your business</p>
                </div>

                <div className="bg-white shadow-xl rounded-2xl overflow-hidden">
                    {/* Stepper */}
                    <div className="flex border-b border-gray-100">
                        <div className={`flex-1 py-4 text-center font-semibold ${step === 1 ? 'text-red-600 border-b-2 border-red-600' : 'text-gray-400'}`}>
                            1. Verification
                        </div>
                        <div className={`flex-1 py-4 text-center font-semibold ${step === 2 ? 'text-red-600 border-b-2 border-red-600' : 'text-gray-400'}`}>
                            2. Restaurant Info
                        </div>
                    </div>

                    <div className="p-8">
                        {error && (
                            <div className="mb-6 bg-red-50 border-l-4 border-red-400 p-4 text-red-700">
                                {error}
                            </div>
                        )}

                        {step === 1 ? (
                            <div className="max-w-md mx-auto">
                                {!otpSent ? (
                                    <form onSubmit={handleSendOtp} className="space-y-6">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700">Owner Name</label>
                                            <input
                                                type="text"
                                                required
                                                className="mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-red-500 focus:border-red-500 py-3 px-4 bg-gray-50 border"
                                                placeholder="Enter full name"
                                                value={name}
                                                onChange={(e) => setName(e.target.value)}
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700">Mobile Number</label>
                                            <div className="mt-1 flex">
                                                <span className="inline-flex items-center px-4 rounded-l-lg border border-r-0 border-gray-300 bg-gray-100 text-gray-500">
                                                    +91
                                                </span>
                                                <input
                                                    type="tel"
                                                    required
                                                    className="block w-full border-gray-300 rounded-r-lg shadow-sm focus:ring-red-500 focus:border-red-500 py-3 px-4 bg-gray-50 border"
                                                    placeholder="10-digit number"
                                                    value={mobile}
                                                    onChange={(e) => setMobile(e.target.value.replace(/\D/g, '').slice(0, 10))}
                                                />
                                            </div>
                                        </div>
                                        <button
                                            type="submit"
                                            disabled={loading || mobile.length < 10}
                                            className="w-full py-4 bg-red-600 text-white rounded-lg font-bold text-lg hover:bg-red-700 transition transform hover:scale-[1.01] disabled:opacity-50"
                                        >
                                            {loading ? 'Sending OTP...' : 'Send OTP'}
                                        </button>
                                        <p className="text-center text-sm text-gray-500">
                                            Already an owner? <Link to="/restaurant/login" className="text-red-600 font-bold">Login here</Link>
                                        </p>
                                    </form>
                                ) : (
                                    <form onSubmit={handleVerifyOtp} className="space-y-6 text-center">
                                        <p className="text-gray-600">Enter the 6-digit code sent to <b>+91 {mobile}</b></p>
                                        <input
                                            type="text"
                                            required
                                            maxLength="6"
                                            className="block w-full border-gray-300 rounded-lg shadow-sm focus:ring-red-500 focus:border-red-500 py-4 text-center text-3xl tracking-widest bg-gray-50 border"
                                            placeholder="000000"
                                            value={otp}
                                            onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                                        />
                                        <button
                                            type="submit"
                                            disabled={loading || otp.length < 6}
                                            className="w-full py-4 bg-black text-white rounded-lg font-bold text-lg hover:bg-gray-800 transition disabled:opacity-50"
                                        >
                                            {loading ? 'Verifying...' : 'Verify & Continue'}
                                        </button>
                                        <button type="button" onClick={() => setOtpSent(false)} className="text-gray-500 hover:text-gray-700 text-sm">
                                            Change Number
                                        </button>
                                    </form>
                                )}
                            </div>
                        ) : (
                            <form onSubmit={handleRestaurantSubmit} className="space-y-8">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="col-span-2">
                                        <h3 className="text-lg font-bold text-gray-900 border-b pb-2 mb-4">Restaurant Basics</h3>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Restaurant Name</label>
                                        <input
                                            name="name"
                                            required
                                            className="mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-red-500 focus:border-red-500 py-2 px-3 bg-gray-50 border"
                                            onChange={handleChange}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Cuisine Type (e.g. North Indian, Pizza)</label>
                                        <input
                                            name="cuisine"
                                            required
                                            className="mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-red-500 focus:border-red-500 py-2 px-3 bg-gray-50 border"
                                            onChange={handleChange}
                                        />
                                    </div>
                                    <div className="col-span-2">
                                        <label className="block text-sm font-medium text-gray-700">Complete Address</label>
                                        <textarea
                                            name="address"
                                            required
                                            rows="2"
                                            className="mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-red-500 focus:border-red-500 py-2 px-3 bg-gray-50 border"
                                            onChange={handleChange}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">City</label>
                                        <input
                                            name="city"
                                            required
                                            className="mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-red-500 focus:border-red-500 py-2 px-3 bg-gray-50 border"
                                            onChange={handleChange}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">State</label>
                                        <input
                                            name="state"
                                            required
                                            className="mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-red-500 focus:border-red-500 py-2 px-3 bg-gray-50 border"
                                            onChange={handleChange}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Pincode</label>
                                        <input
                                            name="pincode"
                                            required
                                            className="mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-red-500 focus:border-red-500 py-2 px-3 bg-gray-50 border"
                                            onChange={handleChange}
                                        />
                                    </div>

                                    <div className="col-span-2">
                                        <h3 className="text-lg font-bold text-gray-900 border-b pb-2 mb-4 mt-4">Document Verification</h3>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">GST Number</label>
                                        <input
                                            name="gst_number"
                                            required
                                            className="mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-red-500 focus:border-red-500 py-2 px-3 bg-gray-50 border"
                                            placeholder="22AAAAA0000A1Z5"
                                            onChange={handleChange}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">PAN Number</label>
                                        <input
                                            name="pan_number"
                                            required
                                            className="mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-red-500 focus:border-red-500 py-2 px-3 bg-gray-50 border"
                                            placeholder="ABCDE1234F"
                                            onChange={handleChange}
                                        />
                                    </div>
                                    <div className="col-span-2">
                                        <label className="block text-sm font-medium text-gray-700">FSSAI License Number</label>
                                        <input
                                            name="fssai_license"
                                            required
                                            className="mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-red-500 focus:border-red-500 py-2 px-3 bg-gray-50 border"
                                            placeholder="14-digit license number"
                                            onChange={handleChange}
                                        />
                                    </div>
                                </div>

                                <div className="flex justify-between items-center pt-6 border-t border-gray-100">
                                    <p className="text-sm text-gray-500 max-w-xs">By clicking register, you agree to our Partner Terms & Conditions.</p>
                                    <button
                                        type="submit"
                                        disabled={loading}
                                        className="px-10 py-4 bg-green-600 text-white rounded-lg font-bold text-lg hover:bg-green-700 transition shadow-lg disabled:opacity-50"
                                    >
                                        {loading ? 'Submitting...' : 'Register Restaurant'}
                                    </button>
                                </div>
                            </form>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RestaurantSignup;
