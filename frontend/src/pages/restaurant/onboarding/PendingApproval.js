
import React from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../../../components/Navbar';

const PendingApproval = () => {
    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            <Navbar />
            <div className="flex-grow flex items-center justify-center p-4">
                <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center border border-gray-100">
                    <div className="w-24 h-24 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-6">
                        <span className="text-4xl">⏳</span>
                    </div>

                    <h1 className="text-2xl font-extrabold text-gray-900 mb-2">Application Under Review</h1>
                    <p className="text-gray-600 mb-8">
                        Thanks for registering! Our team is currently reviewing your restaurant details and documents. This usually takes 24-48 hours.
                    </p>

                    <div className="bg-yellow-50 rounded-xl p-4 mb-8 text-left">
                        <h3 className="text-sm font-bold text-yellow-800 uppercase tracking-wide mb-2">What happens next?</h3>
                        <ul className="text-sm text-yellow-700 space-y-2 list-disc list-inside">
                            <li>We verify your FSSAI & GST documents</li>
                            <li>Our team approves your menu</li>
                            <li>You get access to the dashboard</li>
                        </ul>
                    </div>

                    <Link to="/" className="text-red-600 font-bold hover:text-red-700">
                        Back to Home
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default PendingApproval;
