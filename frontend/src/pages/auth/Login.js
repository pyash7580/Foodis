import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar';
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

    const { login, sendOtp, verifyOtp } = useAuth();
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
            if (res.otp) {
                toast.custom((t) => (
                    <div className={`${t.visible ? 'animate-enter' : 'animate-leave'} max-w-md w-full bg-white shadow-lg rounded-lg pointer-events-auto flex ring-1 ring-black ring-opacity-5`}>
                        <div className="flex-1 w-0 p-4">
                            <div className="flex items-start">
                                <div className="flex-shrink-0 pt-0.5">
                                    <div className="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
                                        <span className="text-xl">💬</span>
                                    </div>
                                </div>
                                <div className="ml-3 flex-1">
                                    <p className="text-sm font-medium text-gray-900">Foodis OTP</p>
                                    <p className="mt-1 text-sm text-gray-500">
                                        Your verification code is{' '}
                                        <span className="font-bold text-gray-900 tracking-wider">{res.otp}</span>
                                    </p>
                                </div>
                            </div>
                        </div>
                        <div className="flex border-l border-gray-200">
                            <button
                                onClick={() => toast.dismiss(t.id)}
                                className="w-full border border-transparent rounded-none rounded-r-lg p-4 flex items-center justify-center text-sm font-medium text-indigo-600 hover:text-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                ), { duration: 30000 });
            }
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
        <div className="min-h-screen bg-gray-50 flex flex-col">
            <Navbar />

            <div className="flex-grow flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
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