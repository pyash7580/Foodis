
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import toast from 'react-hot-toast';

const RestaurantLogin = () => {
    const [loginMethod, setLoginMethod] = useState('otp'); // 'otp' or 'password'
    const [step, setStep] = useState('input'); // 'input', 'otp_verify'
    const [loading, setLoading] = useState(false);

    // Form States
    const [mobile, setMobile] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [otp, setOtp] = useState('');
    const [resendTimer, setResendTimer] = useState(0);

    const { login, sendOtp, verifyOtp } = useAuth();
    const navigate = useNavigate();

    // Countdown Timer logic
    React.useEffect(() => {
        let interval;
        if (resendTimer > 0) {
            interval = setInterval(() => {
                setResendTimer(prev => prev - 1);
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [resendTimer]);

    const handleSendOtp = async (e) => {
        e.preventDefault();
        if (mobile.length !== 10) {
            toast.error("Please enter a valid 10-digit mobile number");
            return;
        }
        setLoading(true);
        const res = await sendOtp(mobile, 'mobile');

        if (res.success) {
            setStep('otp_verify');
            setResendTimer(30); // 30s countdown
            toast.success("OTP sent successfully");
            if (res.otp) {
                // Dev helper - Show OTP in toast for easy testing
                toast.custom((t) => (
                    <div className="bg-white shadow-xl rounded-lg p-4 border-l-4 border-red-500 animate-in slide-in-from-top-5">
                        <p className="font-bold text-gray-800">Test OTP: {res.otp}</p>
                    </div>
                ), { duration: 30000 });
                console.log("OTP:", res.otp);
            }
        } else {
            toast.error(res.error || "Failed to send OTP");
        }
        setLoading(false);
    };

    const handleVerifyOtp = async (e) => {
        e.preventDefault();
        setLoading(true);
        // Verify with 'RESTAURANT' role check
        const res = await verifyOtp(mobile, otp, 'mobile', '', 'RESTAURANT');

        if (res.success) {
            toast.success("Logged in successfully");
            // Navigation handled by status check logic in ProtectedRoute or AuthContext
            // For now, force navigation to root restaurant route which serves as the controller
            navigate('/restaurant/');
        } else {
            if (res.error === "User not registered" || res.code === "NOT_REGISTERED") {
                toast.error("Restaurant not registered! Please contact admin to add your restaurant.", { duration: 4000 });
                // DISABLED: No public restaurant signup - only admin can add restaurants
            } else if (res.error === "ROLE_MISMATCH") {
                toast.error(res.message || "This number is registered with a different role. Please use the correct login page.", { duration: 5000 });
            } else {
                toast.error(res.error || "Invalid OTP");
            }
        }
        setLoading(false);
    };

    const handleEmailLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        const res = await login(email, password); // Login usually checks basic auth

        if (res.success) {
            // We need to double check role here if login doesn't return user obj immediately to validate role
            // But Assuming standard JWT login, we proceed.
            toast.success("Welcome back!");
            navigate('/restaurant/');
        } else {
            toast.error(res.error || "Invalid credentials");
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-white">
            <div className="relative isolate pt-14">
                {/* Background Pattern */}
                <div className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80">
                    <div className="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-[#ff80b5] to-[#9089fc] opacity-30 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]"></div>
                </div>

                <div className="mx-auto max-w-md py-12 px-6 lg:px-8">
                    <div className="bg-white rounded-3xl shadow-xl overflow-hidden border border-gray-100">
                        <div className="px-8 pt-8 pb-6 text-center">
                            <h2 className="text-3xl font-black text-gray-900 tracking-tight">Partner Login</h2>
                            <p className="text-gray-500 mt-2 font-medium">Manage your restaurant seamlessly</p>
                        </div>

                        <div className="px-8 pb-8">
                            {/* Login Method Toggle */}
                            {step === 'input' && (
                                <div className="flex bg-gray-50 p-1.5 rounded-xl mb-8 border border-gray-100">
                                    <button
                                        onClick={() => setLoginMethod('otp')}
                                        className={`flex-1 py-2.5 text-sm font-bold rounded-lg transition-all duration-200 ${loginMethod === 'otp' ? 'bg-white text-red-600 shadow-sm ring-1 ring-gray-200' : 'text-gray-500 hover:text-gray-700'}`}
                                    >
                                        Mobile OTP
                                    </button>
                                    <button
                                        onClick={() => setLoginMethod('password')}
                                        className={`flex-1 py-2.5 text-sm font-bold rounded-lg transition-all duration-200 ${loginMethod === 'password' ? 'bg-white text-red-600 shadow-sm ring-1 ring-gray-200' : 'text-gray-500 hover:text-gray-700'}`}
                                    >
                                        Email Login
                                    </button>
                                </div>
                            )}

                            {/* Forms */}
                            {step === 'input' && loginMethod === 'otp' && (
                                <form onSubmit={handleSendOtp} className="space-y-5">
                                    <div>
                                        <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Mobile Number</label>
                                        <div className="relative flex items-center">
                                            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                                <span className="text-gray-500 font-bold border-r border-gray-200 pr-3">+91</span>
                                            </div>
                                            <input
                                                type="tel"
                                                className="block w-full pl-20 pr-4 py-3.5 bg-gray-50 border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500 focus:bg-white transition font-bold text-gray-900 text-lg placeholder-gray-300"
                                                placeholder="Enter 10-digit number"
                                                value={mobile}
                                                onChange={(e) => setMobile(e.target.value.replace(/\D/g, '').slice(0, 10))}
                                                autoFocus
                                            />
                                        </div>
                                    </div>
                                    <button
                                        type="submit"
                                        disabled={loading || mobile.length !== 10}
                                        className="w-full bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-4 rounded-xl shadow-lg shadow-red-100 transition-all duration-200 transform active:scale-[0.98]"
                                    >
                                        {loading ? <span className="animate-pulse">Sending OTP...</span> : 'Send Verification Code'}
                                    </button>
                                </form>
                            )}

                            {step === 'otp_verify' && (
                                <form onSubmit={handleVerifyOtp} className="space-y-6 text-center animate-in slide-in-from-right-8 duration-300">
                                    <div>
                                        <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl">
                                            📩
                                        </div>
                                        <h3 className="text-lg font-bold text-gray-900">Enter Verification Code</h3>
                                        <p className="text-sm text-gray-500 mt-1">
                                            We sent a code to <span className="font-bold text-gray-900">+91 {mobile}</span>
                                        </p>
                                    </div>

                                    <div className="flex justify-center">
                                        <input
                                            type="text"
                                            maxLength="6"
                                            className="block w-full text-center py-4 text-3xl font-black tracking-[0.5em] text-gray-900 bg-gray-50 border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500 focus:bg-white transition"
                                            placeholder="••••••"
                                            value={otp}
                                            onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                                            autoFocus
                                        />
                                    </div>

                                    <button
                                        type="submit"
                                        disabled={loading || otp.length < 6}
                                        className="w-full bg-black hover:bg-gray-800 disabled:opacity-50 text-white font-bold py-4 rounded-xl shadow-lg transition-all duration-200"
                                    >
                                        {loading ? 'Verifying...' : 'Verify & Login'}
                                    </button>

                                    <div className="pt-2">
                                        {resendTimer > 0 ? (
                                            <p className="text-xs font-bold text-gray-400">
                                                Resend code in <span className="text-red-500">{resendTimer}s</span>
                                            </p>
                                        ) : (
                                            <button
                                                type="button"
                                                onClick={handleSendOtp}
                                                disabled={loading}
                                                className="text-sm font-black text-red-600 hover:text-red-700"
                                            >
                                                Resend OTP
                                            </button>
                                        )}
                                    </div>

                                    <button
                                        type="button"
                                        onClick={() => { setStep('input'); setOtp(''); setResendTimer(0); }}
                                        className="text-sm font-bold text-gray-400 hover:text-gray-600 transition pt-2"
                                    >
                                        Change Mobile Number
                                    </button>
                                </form>
                            )}

                            {step === 'input' && loginMethod === 'password' && (
                                <form onSubmit={handleEmailLogin} className="space-y-5 animate-in fade-in duration-300">
                                    <div>
                                        <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Email Address</label>
                                        <input
                                            type="email"
                                            required
                                            className="block w-full px-4 py-3.5 bg-gray-50 border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500 focus:bg-white transition font-bold text-gray-900"
                                            placeholder="owner@restaurant.com"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Password</label>
                                        <input
                                            type="password"
                                            required
                                            className="block w-full px-4 py-3.5 bg-gray-50 border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500 focus:bg-white transition font-bold text-gray-900"
                                            placeholder="••••••••"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                        />
                                        <div className="text-right mt-2">
                                            <a href="#" className="text-xs font-bold text-red-600 hover:text-red-700">Forgot Password?</a>
                                        </div>
                                    </div>

                                    <button
                                        type="submit"
                                        disabled={loading}
                                        className="w-full bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white font-bold py-4 rounded-xl shadow-lg shadow-red-100 transition-all duration-200"
                                    >
                                        {loading ? 'Logging in...' : 'Login with Password'}
                                    </button>
                                </form>
                            )}
                        </div>

                        <div className="bg-gray-50 px-8 py-6 text-center border-t border-gray-100">
                            <p className="text-sm font-medium text-gray-600 mb-3">Need to add your restaurant?</p>
                            <p className="text-red-600 font-bold text-base mb-4">
                                Contact Admin to Register
                            </p>
                            <div className="space-y-2 text-sm">
                                <div className="flex items-center justify-center gap-2 text-gray-700">
                                    <span className="text-lg">📞</span>
                                    <a href="tel:+919824948665" className="font-bold hover:text-red-600 transition">
                                        +91 98249 48665
                                    </a>
                                </div>
                                <div className="flex items-center justify-center gap-2 text-gray-700">
                                    <span className="text-lg">📧</span>
                                    <a href="mailto:foodisindia@gmail.com" className="font-bold hover:text-red-600 transition">
                                        foodisindia@gmail.com
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RestaurantLogin;
