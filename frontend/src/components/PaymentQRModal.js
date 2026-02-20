import React, { useEffect, useState } from 'react';

const PaymentQRModal = ({ amount, orderId, onSuccess, onClose }) => {
    const [status, setStatus] = useState('generating'); // generating, scanning, processing, success
    const [timeLeft, setTimeLeft] = useState(300); // 5 minutes

    // Generate UPI Intent Link (Using Razorpay Test VPA for realism in test/demo)
    // In production, this would be a dynamic VPA or Order-specific Intent from backend
    const upiLink = `upi://pay?pa=success@razorpay&pn=Foodis&am=${amount}&tr=${orderId}&cu=INR`;
    const qrApiUrl = `https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(upiLink)}`;

    useEffect(() => {
        // Simulate QR generation delay
        const timer1 = setTimeout(() => {
            setStatus('scanning');
        }, 800);

        // Simulate "User Scanned & Paid" after 6 seconds (Demo Flow)
        // In real app, this would poll an endpoint: /api/orders/{id}/status/
        const timer2 = setTimeout(() => {
            setStatus('processing');
            setTimeout(() => {
                setStatus('success');
                setTimeout(() => {
                    onSuccess();
                }, 1000);
            }, 2000);
        }, 8000);

        return () => {
            clearTimeout(timer1);
            clearTimeout(timer2);
        };
    }, [onSuccess]);

    useEffect(() => {
        if (timeLeft > 0 && status !== 'success') {
            const timer = setInterval(() => setTimeLeft(prev => prev - 1), 1000);
            return () => clearInterval(timer);
        }
    }, [timeLeft, status]);

    const formatTime = (seconds) => {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${m}:${s < 10 ? '0' : ''}${s}`;
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl max-w-sm w-full shadow-2xl overflow-hidden relative animate-fade-in-up">

                {/* Header */}
                <div className="bg-gradient-to-r from-red-600 to-red-700 p-4 flex justify-between items-center text-white">
                    <div>
                        <h3 className="font-bold text-lg">Pay via UPI</h3>
                        <p className="text-xs opacity-90">Order #{orderId}</p>
                    </div>
                    <button onClick={onClose} className="text-white hover:bg-white/20 rounded-full p-1 transition">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                    </button>
                </div>

                {/* Body */}
                <div className="p-8 flex flex-col items-center text-center">

                    {status === 'generating' && (
                        <div className="h-64 flex flex-col items-center justify-center space-y-4">
                            <div className="animate-spin rounded-full h-12 w-12 border-4 border-red-500 border-t-transparent"></div>
                            <p className="text-gray-500 font-medium">Generating QR Code...</p>
                        </div>
                    )}

                    {(status === 'scanning' || status === 'processing' || status === 'success') && (
                        <>
                            <div className="relative group">
                                <div className={`border-4 rounded-xl p-2 ${status === 'success' ? 'border-green-500' : 'border-gray-900'} transition-all duration-500`}>
                                    <img src={qrApiUrl} alt="UPI QR Code" className={`w-64 h-64 rounded-lg mix-blend-multiply ${status === 'processing' ? 'opacity-50 blur-sm' : ''} transition-all duration-500`} />
                                </div>

                                {/* Overlay for Processing */}
                                {status === 'processing' && (
                                    <div className="absolute inset-0 flex flex-col items-center justify-center z-10">
                                        <div className="bg-white rounded-full p-3 shadow-lg">
                                            <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
                                        </div>
                                        <p className="text-blue-900 font-bold mt-2 bg-white/90 px-3 py-1 rounded-full text-sm shadow">Verifying...</p>
                                    </div>
                                )}

                                {/* Overlay for Success */}
                                {status === 'success' && (
                                    <div className="absolute inset-0 flex flex-col items-center justify-center z-10 bg-white/10 backdrop-blur-sm rounded-xl">
                                        <div className="bg-green-100 rounded-full p-4 shadow-xl animate-bounce">
                                            <svg className="w-12 h-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
                                        </div>
                                    </div>
                                )}

                                {/* Logos overlay (Zomato style) */}
                                {status === 'scanning' && (
                                    <div className="absolute -bottom-4 left-1/2 transform -translate-x-1/2 bg-white px-4 py-1 rounded-full shadow border flex space-x-2 items-center">
                                        <span className="text-[10px] font-bold text-gray-400 uppercase">Supported</span>
                                        <div className="flex -space-x-1">
                                            <div className="w-5 h-5 rounded-full bg-gray-100 border border-white"></div>
                                            <div className="w-5 h-5 rounded-full bg-blue-100 border border-white"></div>
                                            <div className="w-5 h-5 rounded-full bg-purple-100 border border-white"></div>
                                        </div>
                                    </div>
                                )}
                            </div>

                            <div className="mt-8 space-y-2">
                                <p className="text-2xl font-bold text-gray-900">₹{parseFloat(amount).toFixed(2)}</p>
                                {status === 'scanning' && (
                                    <p className="text-sm text-gray-500 animate-pulse">Scan with any UPI App to pay</p>
                                )}
                                {status === 'processing' && (
                                    <p className="text-sm text-blue-600 font-bold">Payment detected! Preserving...</p>
                                )}
                                {status === 'success' && (
                                    <p className="text-sm text-green-600 font-bold">Payment Successful!</p>
                                )}
                            </div>
                        </>
                    )}
                </div>

                {/* Footer Timer */}
                <div className="bg-gray-50 p-3 text-center border-t border-gray-100">
                    <p className="text-xs text-gray-400 font-mono">
                        Session expires in <span className="text-red-500 font-bold">{formatTime(timeLeft)}</span>
                    </p>
                </div>
            </div>

            <style jsx>{`
                @keyframes fade-in-up {
                    from { opacity: 0; transform: translateY(20px) scale(0.95); }
                    to { opacity: 1; transform: translateY(0) scale(1); }
                }
                .animate-fade-in-up {
                    animation: fade-in-up 0.3s ease-out forwards;
                }
            `}</style>
        </div>
    );
};

export default PaymentQRModal;
