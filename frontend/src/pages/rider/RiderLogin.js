import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { FaMotorcycle, FaArrowRight, FaExclamationCircle, FaEnvelope, FaLock } from 'react-icons/fa';

const RiderLogin = () => {
    const { login } = useAuth();
    const navigate = useNavigate();

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        if (!email || !password) {
            setError('Please enter your email and password.');
            return;
        }
        setLoading(true);
        try {
            const res = await login(email, password, 'RIDER');
            if (res && res.success) {
                toast.success('Welcome back, Rider! 🏍️');
                navigate('/rider/dashboard');
            } else {
                setError(res?.error || res?.message || 'Invalid email or password.');
            }
        } catch (err) {
            console.error(err);
            setError('Login failed. Please check your credentials.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50 flex flex-col justify-center items-center p-4 relative overflow-hidden">
            {/* Background blobs */}
            <div className="absolute inset-0 opacity-5 pointer-events-none">
                <div className="absolute top-20 left-10 w-72 h-72 bg-red-500 rounded-full blur-3xl"></div>
                <div className="absolute bottom-20 right-10 w-96 h-96 bg-orange-500 rounded-full blur-3xl"></div>
            </div>

            {/* Logo */}
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
                    <h2 className="text-2xl font-black text-gray-900 mb-1">Welcome back</h2>
                    <p className="text-gray-500 mb-8 text-sm">Sign in with your rider credentials.</p>

                    <form onSubmit={handleLogin} className="space-y-4">
                        {/* Email */}
                        <div className="relative">
                            <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                                <FaEnvelope className="text-gray-400" size={15} />
                            </div>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="block w-full pl-11 pr-4 py-4 bg-gray-50 border-2 border-gray-200 rounded-xl text-gray-900 font-medium placeholder-gray-300 focus:outline-none focus:border-red-500 focus:bg-white transition-all"
                                placeholder="rider@foodis.com"
                                autoFocus
                                autoComplete="email"
                            />
                        </div>

                        {/* Password */}
                        <div className="relative">
                            <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                                <FaLock className="text-gray-400" size={15} />
                            </div>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="block w-full pl-11 pr-4 py-4 bg-gray-50 border-2 border-gray-200 rounded-xl text-gray-900 font-medium placeholder-gray-300 focus:outline-none focus:border-red-500 focus:bg-white transition-all"
                                placeholder="Your password"
                                autoComplete="current-password"
                            />
                        </div>

                        {error && (
                            <div className="flex items-center text-red-500 text-sm font-bold bg-red-50 p-3 rounded-lg">
                                <FaExclamationCircle className="mr-2 flex-shrink-0" />
                                {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading || !email || !password}
                            className="w-full flex items-center justify-center bg-red-600 hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-black py-4 rounded-xl text-lg shadow-lg shadow-red-200 transition-all active:scale-95 mt-2"
                        >
                            {loading ? (
                                <span className="animate-pulse">Signing in...</span>
                            ) : (
                                <>Login <FaArrowRight className="ml-2" /></>
                            )}
                        </button>
                    </form>

                    <p className="mt-6 text-center text-xs text-gray-400">
                        Password: <span className="font-bold text-gray-600">FirstName@</span> &nbsp;·&nbsp; e.g. <span className="font-bold text-gray-600">Rakesh@</span>
                    </p>
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
