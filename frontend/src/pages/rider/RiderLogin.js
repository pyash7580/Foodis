import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { FaMotorcycle, FaArrowRight, FaEdit, FaExclamationCircle } from 'react-icons/fa';

const RiderLogin = () => {
    const { sendOtp, verifyOtp } = useAuth();
    const navigate = useNavigate();

    // State
    const [step, setStep] = useState(1); // 1: Phone, 2: OTP
    const [phone, setPhone] = useState('');
    const [otp, setOtp] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [timer, setTimer] = useState(30);

    // Timer Logic
    useEffect(() => {
        let interval;
        if (step === 2 && timer > 0) {
            interval = setInterval(() => setTimer((prev) => prev - 1), 1000);
        }
        return () => clearInterval(interval);
    }, [step, timer]);

    // Step 1: Send OTP
    const handleSendOTP = async (e) => {
        e.preventDefault();
        setError('');

        // Validation: 10 Digits
        if (phone.length !== 10) {
            setError('Please enter a valid 10-digit mobile number.');
            return;
        }

        setLoading(true);
        console.log("Sending OTP to:", phone);

        const res = await sendOtp(phone, 'mobile'); // Ensure backend handles 'mobile'
        setLoading(false);

        if (res.success) {
            setStep(2);
            setTimer(30);
            setOtp(''); // Clear previous OTP if any

            // Dev Experience: Toast the OTP if returned (for testing)
            if (res.otp) {
                toast.success(`OTP Sent: ${res.otp}`, { icon: '📲' });
            } else {
                toast.success('OTP sent successfully!');
            }
        } else {
            setError(res.error || 'Failed to send OTP. Please try again.');
        }
    };

    // Step 2: Verification
    const handleVerifyOTP = async (e) => {
        e.preventDefault();
        setError('');

        if (otp.length !== 6) {
            setError('Please enter the 6-digit OTP.');
            return;
        }

        setLoading(true);
        try {
            const res = await verifyOtp(phone, otp, 'mobile', '', 'RIDER');

            if (res.success) {
                if (res.action === 'REGISTER') {
                    setError('Rider account not found. Please contact admin to register your rider profile.');
                    setLoading(false);
                    return;
                }

                const redirect = res.redirect_to || res.redirect;
                const step = res.step;
                const state = res.state;
                console.log("Login Success. Redirection:", redirect, "Step:", step, "State:", state);

                toast.success('Verified Successfully!');

                // Strict Redirection Logic based on backend response
                switch (redirect) {
                    case 'dashboard':
                        navigate('/rider/dashboard');
                        break;
                    case 'status':
                        // Handling UNDER_REVIEW
                        navigate('/rider/status');
                        break;
                    case 'onboarding':
                        // Resumable onboarding
                        // Even if multi-page, we can pass step via state or handle in /rider/onboarding
                        navigate('/rider/onboarding', { state: { step } });
                        break;
                    case 'rejected':
                        navigate('/rider/status'); // Redirect to status which will show rejection
                        break;
                    case 'blocked':
                        navigate('/rider/status');
                        break;
                    default:
                        navigate('/rider/onboarding');
                        break;
                }
            } else {
                setError(res.message || res.error || 'Invalid OTP. Please try again.');
            }
        } catch (err) {
            console.error(err);
            setError('Something went wrong. Please check your connection.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50 flex flex-col justify-center items-center p-4 relative overflow-hidden">
            {/* Background Pattern */}
            <div className="absolute inset-0 opacity-5">
                <div className="absolute top-20 left-10 w-72 h-72 bg-red-500 rounded-full blur-3xl"></div>
                <div className="absolute bottom-20 right-10 w-96 h-96 bg-orange-500 rounded-full blur-3xl"></div>
            </div>

            {/* Logo / Brand */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="mb-8 text-center relative z-10"
            >
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-red-500 to-orange-500 text-white mb-4 shadow-2xl shadow-red-200">
                    <FaMotorcycle size={36} />
                </div>
                <h1 className="text-4xl font-black text-gray-900 tracking-tight mb-1">FOODIS<span className="text-red-600">.</span></h1>
                <p className="text-gray-600 font-semibold text-sm tracking-wide">Delivery Partner App</p>
            </motion.div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="glass-morphism w-full max-w-md rounded-3xl shadow-2xl overflow-hidden border border-white/20 relative z-10"
            >
                <div className="p-8">
                    <AnimatePresence mode="wait">
                        {step === 1 ? (
                            <motion.div
                                key="step1"
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 20 }}
                            >
                                <h2 className="text-2xl font-black text-gray-900 mb-2">Login</h2>
                                <p className="text-gray-500 mb-8">Enter your mobile number to start earning.</p>

                                <form onSubmit={handleSendOTP} className="space-y-6">
                                    <div className="relative group">
                                        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                            <span className="text-gray-400 font-bold text-lg select-none">+91</span>
                                            <div className="h-6 w-px bg-gray-300 mx-3"></div>
                                        </div>
                                        <input
                                            type="tel"
                                            value={phone}
                                            onChange={(e) => {
                                                const val = e.target.value.replace(/\D/g, '');
                                                if (val.length <= 10) setPhone(val);
                                            }}
                                            className="block w-full pl-20 pr-4 py-4 bg-gray-50 border-2 border-gray-200 rounded-xl text-gray-900 font-bold text-xl placeholder-gray-300 focus:outline-none focus:border-red-500 focus:bg-white transition-all"
                                            placeholder="00000 00000"
                                            autoFocus
                                        />
                                    </div>

                                    {error && (
                                        <div className="flex items-center text-red-500 text-sm font-bold bg-red-50 p-3 rounded-lg">
                                            <FaExclamationCircle className="mr-2" />
                                            {error}
                                        </div>
                                    )}

                                    <button
                                        type="submit"
                                        disabled={loading || phone.length < 10}
                                        className="w-full flex items-center justify-center bg-red-600 hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-black py-4 rounded-xl text-lg shadow-lg shadow-red-200 transition-all active:scale-95"
                                    >
                                        {loading ? (
                                            <span className="animate-pulse">Sending OTP...</span>
                                        ) : (
                                            <>Get OTP <FaArrowRight className="ml-2" /></>
                                        )}
                                    </button>
                                </form>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="step2"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                            >
                                <div className="flex justify-between items-start mb-6">
                                    <div>
                                        <h2 className="text-2xl font-black text-gray-900">Verification</h2>
                                        <div className="flex items-center mt-1 cursor-pointer group" onClick={() => setStep(1)}>
                                            <p className="text-gray-500 mr-2 group-hover:text-red-600 transition">Sent to <span className="font-bold text-gray-900">+91 {phone}</span></p>
                                            <FaEdit className="text-gray-400 text-xs group-hover:text-red-600 transition" />
                                        </div>
                                    </div>
                                </div>

                                <form onSubmit={handleVerifyOTP} className="space-y-6">
                                    <input
                                        type="text"
                                        value={otp}
                                        onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                                        className="block w-full text-center py-4 bg-white border-2 border-gray-200 rounded-xl text-gray-900 font-black text-3xl tracking-[0.5em] placeholder-gray-200 focus:outline-none focus:border-red-500 transition-all"
                                        placeholder="••••••"
                                        autoFocus
                                    />

                                    <div className="flex justify-between items-center text-sm font-bold">
                                        <span className="text-gray-400">Not received?</span>
                                        <button
                                            type="button"
                                            onClick={handleSendOTP}
                                            disabled={timer > 0 || loading}
                                            className={`${timer > 0 ? 'text-gray-300 cursor-not-allowed' : 'text-red-600 hover:underline'}`}
                                        >
                                            {timer > 0 ? `Resend in ${timer}s` : 'Resend OTP'}
                                        </button>
                                    </div>

                                    {error && (
                                        <div className="flex items-center text-red-500 text-sm font-bold bg-red-50 p-3 rounded-lg justify-center">
                                            <FaExclamationCircle className="mr-2" />
                                            {error}
                                        </div>
                                    )}

                                    <button
                                        type="submit"
                                        disabled={loading || otp.length < 6}
                                        className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-black py-4 rounded-xl text-lg shadow-lg shadow-red-200 transition-all active:scale-95 flex justify-center items-center"
                                    >
                                        {loading ? 'Verifying...' : 'Verify & Login'}
                                    </button>
                                </form>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </motion.div>

            <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.8 }}
                className="mt-8 text-gray-400 text-xs font-bold uppercase tracking-widest relative z-10"
            >© 2026 Foodis Logistics</motion.p>
        </div>
    );
};

export default RiderLogin;
