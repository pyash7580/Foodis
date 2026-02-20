
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../../config';
import { useAuth } from '../../contexts/AuthContext';
import toast from 'react-hot-toast';
import { FaShieldAlt, FaLock, FaUserShield } from 'react-icons/fa';

const AdminLogin = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth(); // We can reuse login from context but need to be careful about state key
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            // Direct API call to ensure we handle the response specific to admin
            // Effectively mimicking authContext login but forcing explicit checks if needed
            // Actually, using context login is fine as long as we are on /admin/login path, 
            // the context will pick up 'token_admin' key automatically due to getStorageKey

            const res = await axios.post(`${API_BASE_URL}/api/auth/login/`, { email, password });
            const { token, user } = res.data;

            if (user.role !== 'ADMIN' && !user.is_superuser) {
                toast.error("Access Denied: You do not have admin privileges.");
                setLoading(false);
                return;
            }

            // Save specifically to token_admin
            localStorage.setItem('token_admin', token);

            // Navigate to dashboard
            toast.success("Welcome, Super Admin");
            navigate('/admin/dashboard');

        } catch (err) {
            console.error(err);
            toast.error(err.response?.data?.error || "Login Failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-900 px-4">
            <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl overflow-hidden">
                <div className="bg-black py-8 text-center text-white">
                    <FaShieldAlt className="text-5xl mx-auto mb-2 text-red-600" />
                    <h1 className="text-2xl font-bold tracking-wider uppercase">Foodis Admin</h1>
                    <p className="text-gray-400 text-sm mt-1">Super Authority Access</p>
                </div>

                <form onSubmit={handleLogin} className="p-8 space-y-6">
                    <div>
                        <label className="block text-gray-600 font-bold mb-2">Username / Email</label>
                        <div className="relative">
                            <FaUserShield className="absolute top-4 left-4 text-gray-400" />
                            <input
                                type="text"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full pl-12 pr-4 py-3 rounded-xl border border-gray-200 focus:border-red-600 focus:ring-1 focus:ring-red-600 outline-none transition"
                                placeholder="admin@foodis.com"
                                required
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-gray-600 font-bold mb-2">Password</label>
                        <div className="relative">
                            <FaLock className="absolute top-4 left-4 text-gray-400" />
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full pl-12 pr-4 py-3 rounded-xl border border-gray-200 focus:border-red-600 focus:ring-1 focus:ring-red-600 outline-none transition"
                                placeholder="••••••••"
                                required
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-black text-white py-4 rounded-xl font-bold text-lg hover:bg-gray-800 transition transform active:scale-95 disabled:opacity-50"
                    >
                        {loading ? 'Verifying Credentials...' : 'Access Panel'}
                    </button>

                    <div className="text-center text-xs text-gray-400 mt-4">
                        Secure Connection • IP Logged • Unauthorized Access Prohibited
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AdminLogin;
