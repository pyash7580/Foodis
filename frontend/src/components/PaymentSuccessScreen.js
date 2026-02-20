
import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import Navbar from './Navbar';
import Confetti from 'react-confetti';

const PaymentSuccessScreen = () => {
    const { orderId } = useParams();
    const navigate = useNavigate();
    const [showConfetti, setShowConfetti] = useState(true);
    const [windowSize, setWindowSize] = useState({
        width: window.innerWidth,
        height: window.innerHeight,
    });

    useEffect(() => {
        const handleResize = () => {
            setWindowSize({
                width: window.innerWidth,
                height: window.innerHeight,
            });
        };

        window.addEventListener('resize', handleResize);

        // Stop confetti after 5 seconds
        const timer = setTimeout(() => {
            setShowConfetti(false);
        }, 5000);

        return () => {
            window.removeEventListener('resize', handleResize);
            clearTimeout(timer);
        };
    }, []);

    return (
        <div className="min-h-screen bg-white flex flex-col font-sans">
            <Navbar />
            {showConfetti && (
                <Confetti
                    width={windowSize.width}
                    height={windowSize.height}
                    recycle={false}
                    numberOfPieces={500}
                    gravity={0.2}
                />
            )}
            <div className="flex-grow flex flex-col items-center justify-center p-6 animate-in fade-in zoom-in duration-500">
                <div className="max-w-md w-full text-center">
                    {/* Success Animation Container */}
                    <div className="relative mb-10">
                        <div className="w-32 h-32 bg-green-50 rounded-full flex items-center justify-center mx-auto relative z-10 animate-bounce">
                            <svg className="w-16 h-16 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="4" d="M5 13l4 4L19 7" />
                            </svg>
                        </div>
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 bg-green-100 rounded-full opacity-20 animate-ping"></div>
                    </div>

                    <h1 className="text-4xl font-black text-gray-900 mb-4 tracking-tight">Order Placed!</h1>
                    <p className="text-gray-500 font-bold mb-2 uppercase tracking-widest text-xs">Order ID</p>
                    <p className="text-2xl font-black text-red-600 mb-8 px-6 py-2 bg-red-50 rounded-full inline-block">
                        #{orderId.includes('_') ? orderId.split('_').slice(-1)[0] : orderId}
                    </p>

                    <div className="bg-gray-50 rounded-3xl p-6 mb-10 border border-gray-100 text-left">
                        <div className="flex items-center mb-4">
                            <span className="text-2xl mr-3">🛵</span>
                            <div>
                                <p className="font-black text-gray-900 leading-none">Arriving in 35 mins</p>
                                <p className="text-sm text-gray-400 font-bold mt-1">Restaurant is preparing your food</p>
                            </div>
                        </div>
                        <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden">
                            <div className="bg-green-600 h-full w-1/3 rounded-full animate-pulse"></div>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <button
                            onClick={() => navigate(`/client/track/${orderId}`)}
                            className="block w-full bg-black text-white py-5 rounded-2xl font-black text-lg shadow-xl hover:scale-[1.02] transition-transform active:scale-95 flex items-center justify-center"
                        >
                            TRACK LIVE ORDER 🛵
                        </button>
                        <Link
                            to="/client"
                            className="block w-full bg-white text-gray-500 py-3 rounded-xl font-bold hover:text-gray-900 transition"
                        >
                            Back to Home
                        </Link>
                    </div>
                </div>

                <div className="mt-12 text-gray-300 text-[10px] font-black uppercase tracking-[0.2em]">
                    Thank you for choosing Foodis
                </div>
            </div>
        </div>
    );
};

export default PaymentSuccessScreen;
