
import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Navbar from '../../components/Navbar';
import { useAuth } from '../../contexts/AuthContext';
import toast from 'react-hot-toast';

const Register = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { register } = useAuth();

    // Get phone from navigation state (passed from Login.js)
    const [phone] = useState(location.state?.phone || '');
    const [email, setEmail] = useState(location.state?.email || '');
    const [name, setName] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!phone) {
            toast.error("Please verify your mobile number first");
            navigate('/login');
        }
    }, [phone, navigate]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!name.trim()) {
            setError('Name is required');
            return;
        }

        setLoading(true);
        setError('');

        const res = await register({
            phone,
            name,
            email,
            role: 'CLIENT'
        });

        if (res.success) {
            toast.success("Welcome to Foodis!");
            navigate('/client');
        } else {
            setError(res.error);
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
                            Complete Your Profile
                        </h2>
                        <p className="mt-2 text-center text-sm text-gray-600">
                            Just a few more details to get you started.
                        </p>
                    </div>

                    {error && (
                        <div className="bg-red-50 text-red-700 p-3 rounded text-sm text-center">
                            {error}
                        </div>
                    )}

                    <form className="space-y-6" onSubmit={handleSubmit}>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Mobile Number</label>
                            <input
                                type="text"
                                disabled
                                className="mt-1 block w-full px-3 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-500 sm:text-sm cursor-not-allowed"
                                value={`+91 ${phone}`}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Full Name <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="text"
                                required
                                className="mt-1 appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-red-500 focus:border-red-500 sm:text-sm"
                                placeholder="Enter your full name"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Email Address <span className="text-gray-400 font-normal">(Optional)</span>
                            </label>
                            <input
                                type="email"
                                className="mt-1 appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-red-500 focus:border-red-500 sm:text-sm"
                                placeholder="Enter your email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>

                        <div>
                            <button
                                type="submit"
                                disabled={loading || !name.trim()}
                                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                            >
                                {loading ? 'Saving...' : 'Finish Registration'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Register;
