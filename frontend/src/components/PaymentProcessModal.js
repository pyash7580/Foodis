
import React from 'react';

const PaymentProcessModal = ({ isOpen, status, message }) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm">
            <div className="bg-white rounded-3xl p-8 max-w-sm w-full mx-4 shadow-2xl transform transition-all animate-in fade-in zoom-in duration-300">
                <div className="flex flex-col items-center text-center">
                    {/* Zomato-like loader */}
                    <div className="relative w-24 h-24 mb-6">
                        <div className="absolute inset-0 border-4 border-red-100 rounded-full"></div>
                        <div className="absolute inset-0 border-4 border-red-600 rounded-full border-t-transparent animate-spin"></div>
                        <div className="absolute inset-0 flex items-center justify-center">
                            <span className="text-3xl">🍕</span>
                        </div>
                    </div>

                    <h2 className="text-2xl font-black text-gray-900 mb-2">
                        {status === 'processing' ? 'Processing Payment' :
                            status === 'initiating' ? 'Initiating Gateway' :
                                status === 'verifying' ? 'Verifying Payment' : 'Please Wait'}
                    </h2>

                    <p className="text-gray-500 font-medium">
                        {message || "Don't press back or close the app"}
                    </p>

                    <div className="mt-8 flex space-x-2">
                        <div className="w-2 h-2 bg-red-600 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
                        <div className="w-2 h-2 bg-red-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-2 h-2 bg-red-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PaymentProcessModal;
