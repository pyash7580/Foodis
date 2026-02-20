
import React from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../../../components/Navbar';

const Rejected = () => {
    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            <Navbar />
            <div className="flex-grow flex items-center justify-center p-4">
                <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center border border-gray-100">
                    <div className="w-24 h-24 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
                        <span className="text-4xl">❌</span>
                    </div>

                    <h1 className="text-2xl font-extrabold text-gray-900 mb-2">Application Not Approved</h1>
                    <p className="text-gray-600 mb-8">
                        Unfortunately, your restaurant application could not be approved at this time.
                    </p>

                    <div className="bg-red-50 rounded-xl p-4 mb-8 text-left">
                        <div className="flex items-start">
                            <span className="text-xl mr-3">ℹ️</span>
                            <div>
                                <h3 className="text-sm font-bold text-red-800 uppercase tracking-wide mb-1">Common Reasons</h3>
                                <p className="text-xs text-red-700">Invalid documents, incomplete profile, or service unavailability in your area.</p>
                            </div>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <Link
                            to="/restaurant/help"
                            className="block w-full py-3 bg-red-600 text-white rounded-xl font-bold hover:bg-red-700 transition"
                        >
                            Contact Support
                        </Link>
                        <Link to="/" className="block text-gray-500 font-bold hover:text-gray-700 text-sm">
                            Back to Home
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Rejected;
