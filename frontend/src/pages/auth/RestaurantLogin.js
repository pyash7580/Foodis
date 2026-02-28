
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import toast from 'react-hot-toast';

const RestaurantLogin = () => {
    const [loading, setLoading] = useState(false);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const { login } = useAuth();
    const navigate = useNavigate();

    const handleEmailLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        const res = await login(email, password, 'RESTAURANT');

        if (res.success) {
            toast.success("Welcome back!");
            navigate('/restaurant/');
        } else {
            toast.error(res.message || res.error || "Invalid credentials");
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
                                        <button
                                            type="button"
                                            onClick={() => toast.error("Please contact admin to reset password")}
                                            className="text-xs font-bold text-red-600 hover:text-red-700"
                                        >
                                            Forgot Password?
                                        </button>
                                    </div>
                                </div>

                                <button
                                    type="submit"
                                    disabled={loading || !email || !password}
                                    className="w-full bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white font-bold py-4 rounded-xl shadow-lg shadow-red-100 transition-all duration-200"
                                >
                                    {loading ? 'Logging in...' : 'Login with Password'}
                                </button>
                            </form>
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
