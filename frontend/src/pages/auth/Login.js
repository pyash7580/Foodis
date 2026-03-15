import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import toast from 'react-hot-toast';

const Login = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [step, setStep] = useState('input');

    const [email, setEmail] = useState('');
    const [otp, setOtp] = useState('');
    const [name, setName] = useState('');
    const [isSignup, setIsSignup] = useState(false);
    const [resendTimer, setResendTimer] = useState(0);

    const { sendOtp, verifyOtp } = useAuth();
    const navigate = useNavigate();

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
        if (e && e.preventDefault) e.preventDefault();
        setError('');
        setLoading(true);

        const res = await sendOtp(email);

        if (res.success) {
            setStep('otp');
            setResendTimer(30);
        } else {
            setError(res.error || 'Failed to send OTP. Please try again.');
        }
        setLoading(false);
    };

    const handleVerifyOtp = async (e) => {
        e.preventDefault();
        setError('');

        if (!otp || otp.length < 4) {
            setError('Please enter a valid OTP.');
            return;
        }

        setLoading(true);

        const res = await verifyOtp(email, otp, isSignup ? name : '');

        if (res.success) {
            if (res.action === 'REGISTER') {
                toast.success("OTP Verified! Please complete your profile.");
                navigate('/register', { state: { email: res.email } });
            } else {
                navigate('/client');
            }
        } else {
            setError(res.error || 'Verification failed. Please try again.');
        }
        setLoading(false);
    };


    return (
        <div className="min-h-screen bg-gray-50 flex flex-col relative pb-16 md:pb-0">
            {/* Mobile App Bar */}
            <div className="md:hidden bg-white flex items-center px-4 h-14 border-b border-gray-100 sticky top-0 z-40 shadow-sm">
                <button
                    onClick={() => navigate('/client')}
                    className="p-2 -ml-2 text-gray-800 focus:outline-none"
                >
                    <span className="text-xl leading-none">←</span>
                </button>
                <h1 className="ml-2 text-lg font-black text-gray-900 truncate flex-1">
                    {step === 'otp' ? 'Login' : (isSignup ? 'Sign Up' : 'Login')}
                </h1>
            </div>

            <div className="hidden md:block">
                {/* Desktop placeholder if needed, though ClientLayout manages nav typically */}
                <div className="p-4 bg-white border-b border-gray-100 flex items-center justify-between">
                    <button onClick={() => navigate('/client')} className="text-xl font-black text-red-600">Foodis</button>
                </div>
            </div>

            <div className="flex-grow flex items-center justify-center py-6 md:py-12 px-4 sm:px-6 lg:px-8">
                <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-xl shadow-lg border border-gray-100">
                    <div>
                        <h2 className="mt-2 text-center text-3xl font-extrabold text-gray-900">
                            {step === 'otp' ? 'Enter OTP' : (isSignup ? 'Create Account' : 'Login to Foodis')}
                        </h2>
                        {step !== 'otp' && (
                            <p className="mt-2 text-center text-sm text-gray-600">
                                Access your orders, favorites, and more.
                            </p>
                        )}
                    </div>

                    {error && (
                        <div className="bg-red-50 text-red-700 p-3 rounded text-sm text-center">
                            {error}
                        </div>
                    )}

                    {step === 'input' && (
                        <>
                            <form className="space-y-6" onSubmit={handleSendOtp}>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Email address</label>
                                    <input
                                        type="email"
                                        required
                                        className="mt-1 appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-red-500 focus:border-red-500 focus:z-10 sm:text-sm"
                                        placeholder="Enter your email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value.toLowerCase())}
                                    />
                                </div>

                                {isSignup && (
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Your Full Name <span className="text-red-500">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            required
                                            className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-red-500 focus:border-red-500 focus:z-10 sm:text-sm"
                                            placeholder="Enter your full name"
                                            value={name}
                                            onChange={(e) => setName(e.target.value)}
                                        />
                                    </div>
                                )}

                                <button
                                    type="submit"
                                    disabled={loading || !email || (isSignup && !name.trim())}
                                    className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                                >
                                    {loading ? 'Sending OTP...' : (isSignup ? 'Create Account' : 'Send OTP')}
                                </button>

                                <div className="text-center mt-4">
                                    <p className="text-sm text-gray-600">
                                        {isSignup ? "Already have an account?" : "New to Foodis?"}
                                        <button
                                            type="button"
                                            onClick={() => { setIsSignup(!isSignup); setError(''); }}
                                            className="ml-1 font-bold text-red-600 hover:text-red-500"
                                        >
                                            {isSignup ? "Login Instead" : "Sign Up Now"}
                                        </button>
                                    </p>
                                </div>
                            </form>
                        </>
                    )}

                    {step === 'otp' && (
                        <form className="space-y-6" onSubmit={handleVerifyOtp}>
                            <p className="text-center text-gray-600 text-sm">
                                We sent a code to <br />
                                <span className="font-bold text-gray-900">{email}</span>
                            </p>

                            <div>
                                <input
                                    type="text"
                                    required
                                    maxLength="6"
                                    className="appearance-none rounded-md block w-full px-3 py-3 border border-gray-300 placeholder-gray-400 text-gray-900 text-center text-2xl tracking-widest focus:outline-none focus:ring-red-500 focus:border-red-500"
                                    placeholder="000000"
                                    value={otp}
                                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={loading || otp.length < 4}
                                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-70"
                            >
                                {loading ? 'Verifying...' : 'Verify & Proceed'}
                            </button>

                            <div className="text-center">
                                {resendTimer > 0 ? (
                                    <p className="text-xs text-gray-500 font-medium">
                                        Resend OTP in <span className="text-gray-900 font-bold">{resendTimer}s</span>
                                    </p>
                                ) : (
                                    <button
                                        type="button"
                                        onClick={handleSendOtp}
                                        disabled={loading}
                                        className="text-sm font-bold text-red-600 hover:text-red-700 disabled:opacity-50"
                                    >
                                        Resend OTP
                                    </button>
                                )}
                            </div>

                            <button
                                type="button"
                                onClick={() => { setStep('input'); setOtp(''); setResendTimer(0); setError(''); }}
                                className="w-full text-center text-sm text-gray-500 hover:text-gray-700 pt-2"
                            >
                                Change Email
                            </button>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Login;