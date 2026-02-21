import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaStore } from 'react-icons/fa';

const OrderRequestModal = ({ order, onAccept, onReject }) => {
    const [timer, setTimer] = useState(30);

    useEffect(() => {
        setTimer(30); // Reset timer on new order
        const interval = setInterval(() => {
            setTimer((prev) => {
                if (prev <= 1) {
                    clearInterval(interval);
                    onReject(); // Auto reject
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);
        return () => clearInterval(interval);
    }, [order?.id, onReject]);

    if (!order) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="fixed inset-0 z-[10000] flex items-center justify-center p-6 bg-black/60 backdrop-blur-sm"
            >
                <div className="w-full max-w-sm glass-morphism-dark rounded-[2.5rem] shadow-[0_30px_60px_rgba(0,0,0,0.8)] overflow-hidden border border-white/10 relative">
                    <div className="absolute top-0 left-0 w-full h-1 bg-white/5">
                        <motion.div
                            initial={{ width: "100%" }}
                            animate={{ width: `${(timer / 30) * 100}%` }}
                            transition={{ duration: 1, ease: "linear" }}
                            className="h-full bg-gradient-to-r from-red-500 to-orange-500 shadow-[0_0_15px_rgba(239,68,68,0.5)]"
                        />
                    </div>

                    {/* Header with Timer */}
                    <div className="p-8 flex justify-between items-center bg-gradient-to-b from-white/5 to-transparent">
                        <div>
                            <h3 className="font-black text-2xl text-white tracking-tighter">New Order</h3>
                            <p className="text-[10px] text-orange-400 font-black uppercase tracking-[0.3em] mt-1">Assignment Alert</p>
                        </div>
                        <div className="flex flex-col items-center justify-center w-14 h-14 bg-white/5 rounded-2xl border border-white/5">
                            <span className="font-black text-xl text-white leading-none">{timer}</span>
                            <span className="text-[8px] font-black text-gray-500 uppercase mt-1">SEC</span>
                        </div>
                    </div>

                    <div className="px-8 pb-8 pt-2">
                        {/* Restaurant Info */}
                        <div className="flex items-center mb-8 p-4 bg-white/5 rounded-3xl border border-white/5">
                            <div className="bg-orange-500/20 p-4 rounded-2xl mr-4">
                                <FaStore className="text-orange-400 text-xl" />
                            </div>
                            <div className="flex-1 overflow-hidden">
                                <h4 className="font-black text-white text-lg tracking-tight truncate">{order.restaurant_name}</h4>
                                <p className="text-gray-500 text-[9px] font-black uppercase tracking-widest truncate">{order.restaurant_address}</p>
                            </div>
                        </div>

                        {/* Route Info */}
                        <div className="grid grid-cols-2 gap-4 mb-8">
                            <div className="bg-white/5 p-5 rounded-[1.5rem] border border-white/5 text-center">
                                <p className="text-[8px] text-gray-500 font-black uppercase tracking-widest mb-1">Pickup</p>
                                <p className="font-black text-white text-lg tracking-tight">{order.distance || '2.5'} <span className="text-xs opacity-40">KM</span></p>
                            </div>
                            <div className="bg-white/5 p-5 rounded-[1.5rem] border border-white/5 text-center">
                                <p className="text-[8px] text-gray-500 font-black uppercase tracking-widest mb-1">Earnings</p>
                                <p className="font-black text-emerald-400 text-lg tracking-tight">₹{order.estimated_earning || '45'}</p>
                            </div>
                        </div>

                        {/* Actions */}
                        <div className="space-y-3">
                            <button
                                onClick={() => onAccept(order.id)}
                                className="w-full bg-[#FF3008] text-white font-black py-5 rounded-2xl text-[10px] uppercase tracking-[0.2em] shadow-[0_15px_30px_rgba(255,48,8,0.3)] hover:bg-[#FF6B00] transition-all active:scale-95 border border-white/10"
                            >
                                Accept Assignment
                            </button>
                            <button
                                onClick={onReject}
                                className="w-full bg-white/5 text-gray-500 font-black py-4 rounded-2xl text-[10px] uppercase tracking-[0.2em] hover:bg-white/10 transition-all border border-transparent hover:border-white/5"
                            >
                                Decline
                            </button>
                        </div>
                    </div>
                </div>
            </motion.div>
        </AnimatePresence>
    );
};

export default OrderRequestModal;
