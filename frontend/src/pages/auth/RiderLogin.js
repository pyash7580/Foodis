import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import toast from 'react-hot-toast';
import { FaMotorcycle, FaArrowRight } from 'react-icons/fa';

const RiderLogin = () => {
    const [step, setStep] = useState('input'); // 'input' or 'otp'
    const [mobile, setMobile] = useState('');
    const [otp, setOtp] = useState('');
    const [loading, setLoading] = useState(false);
    const [resendTimer, setResendTimer] = useState(0);

    const { sendOtp, verifyOtp } = useAuth();
    const navigate = useNavigate();

    // Timer logic
    React.useEffect(() => {
        let interval;
        if (resendTimer > 0) {
            interval = setInterval(() => setResendTimer(prev => prev - 1), 1000);
        }
        return () => clearInterval(interval);
    }, [resendTimer]);

    const handleSendOtp = async (e) => {
        e.preventDefault();
        setLoading(true);

        const res = await sendOtp(mobile, 'mobile');
        if (res.success) {
            setStep('otp');
            setResendTimer(30);
            if (res.otp) {
                toast.success(`OTP: ${res.otp}`, { duration: 30000, icon: '🔑' });
            }
        } else {
            toast.error(res.error || "Failed to send OTP");
        }
        setLoading(false);
    };

    const handleVerifyOtp = async (e) => {
        e.preventDefault();
        setLoading(true);

        // Verify with role='RIDER'
        const res = await verifyOtp(mobile, otp, 'mobile', '', 'RIDER');

        if (res.success) {
            toast.success("Welcome back, Rider!");
            // Redirect logic is handled by RiderProtectedRoute usually, but we can force check
            navigate('/rider/dashboard');
        } else {
            toast.error(res.error || "Invalid OTP");
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center p-4 font-jakarta relative overflow-hidden">

            {/* Background Decorations */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 opacity-20">
                <div className="absolute top-10 left-10 w-64 h-64 bg-red-600 rounded-full mix-blend-multiply filter blur-xl animate-blob"></div>
                <div className="absolute top-10 right-10 w-64 h-64 bg-yellow-600 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-2000"></div>
                <div className="absolute -bottom-8 left-20 w-64 h-64 bg-pink-600 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-4000"></div>
            </div>

            <div className="max-w-md w-full bg-white/10 backdrop-blur-lg border border-white/20 rounded-3xl p-8 shadow-2xl z-10 text-white">
                <div className="text-center mb-8">
                    <div className="bg-red-600 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg transform rotate-3">
                        <FaMotorcycle className="text-3xl text-white" />
                    </div>
                    <h1 className="text-3xl font-black tracking-tight">Foodis Rider</h1>
                    <p className="text-gray-400 mt-2 text-sm">Valid Mobile Number required for login</p>
                </div>

                {step === 'input' ? (
                    <form onSubmit={handleSendOtp} className="space-y-6">
                        <div>
                            <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Mobile Number</label>
                            <div className="relative">
                                <span className="absolute left-4 top-3.5 text-gray-400 font-bold">+91</span>
                                <input
                                    type="tel"
                                    value={mobile}
                                    onChange={e => setMobile(e.target.value.replace(/\D/g, '').slice(0, 10))}
                                    className="w-full bg-gray-800/50 border border-gray-700 rounded-xl py-3 pl-12 pr-4 text-white placeholder-gray-600 focus:outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500 transition font-bold tracking-widest"
                                    placeholder="00000 00000"
                                    required
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading || mobile.length !== 10}
                            className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-4 rounded-xl transition-all transform hover:scale-[1.02] flex items-center justify-center disabled:opacity-50 disabled:hover:scale-100"
                        >
                            {loading ? 'Sending...' : <>Get OTP <FaArrowRight className="ml-2" /></>}
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleVerifyOtp} className="space-y-6">
                        <div className="text-center">
                            <p className="text-gray-400 text-sm mb-6">Enter the 6-digit code sent to <br /><span className="text-white font-bold">+91 {mobile}</span></p>

                            <input
                                type="text"
                                value={otp}
                                onChange={e => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                                className="w-full bg-gray-800/50 border border-gray-700 rounded-xl py-4 text-center text-2xl font-bold tracking-[0.5em] text-white focus:outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500 transition"
                                placeholder="••••••"
                                autoFocus
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading || otp.length !== 6}
                            className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-4 rounded-xl transition-all transform hover:scale-[1.02] shadow-lg disabled:opacity-50 disabled:hover:scale-100"
                        >
                            {loading ? 'Verifying...' : 'Verify Login'}
                        </button>

                        <div className="flex justify-between items-center text-sm pt-4">
                            <button
                                type="button"
                                onClick={() => { setStep('input'); setOtp(''); }}
                                className="text-gray-400 hover:text-white transition"
                            >
                                Change Number
                            </button>

                            {resendTimer > 0 ? (
                                <span className="text-gray-500">Resend in {resendTimer}s</span>
                            ) : (
                                <button
                                    type="button"
                                    onClick={handleSendOtp}
                                    className="text-red-400 hover:text-red-300 font-bold transition"
                                >
                                    Resend OTP
                                </button>
                            )}
                        </div>
                    </form>
                )}

                <div className="mt-8 text-center">
                    <p className="text-xs text-gray-500">By logging in, you agree to our Terms & Service Conditions.</p>
                </div>
            </div>
        </div>
    );
};

export default RiderLogin;
