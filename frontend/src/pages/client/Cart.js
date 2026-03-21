
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../../contexts/CartContext';

const Cart = () => {
    const { cartItems, restaurant, updateQuantity, getCartTotal } = useCart();
    const navigate = useNavigate();
    const [mobileShowSummary, setMobileShowSummary] = useState(false);

    const subtotal = getCartTotal();
    const deliveryFee = restaurant ? parseFloat(restaurant.delivery_fee) : 0;
    const taxes = subtotal * 0.05; // 5% tax mock
    const total = subtotal + deliveryFee + taxes;

    if (cartItems.length === 0) {
        return (
            <div className="min-h-screen bg-gray-50 flex flex-col relative pb-16 md:pb-0">
                {/* Mobile App Bar */}
                <div className="md:hidden bg-white flex items-center px-4 h-14 border-b border-gray-100 sticky top-0 z-40">
                    <button onClick={() => navigate(-1)} className="p-2 -ml-2 text-gray-800">
                        <span className="text-xl leading-none">←</span>
                    </button>
                    <h1 className="ml-2 text-lg font-black text-gray-900">Cart</h1>
                </div>

                <div className="flex-grow flex flex-col items-center justify-center p-4">
                    <img src="https://cdni.iconscout.com/illustration/premium/thumb/empty-cart-2130356-1800917.png" alt="Empty Cart" className="w-40 h-40 sm:w-64 sm:h-64 opacity-50 mb-4" />
                    <h2 className="text-xl sm:text-2xl font-bold text-gray-700 mb-2">Your Cart is Empty</h2>
                    <p className="text-gray-500 mb-6 text-center text-sm sm:text-base">Looks like you haven't added anything to your cart yet.</p>
                    <Link to="/client" className="bg-red-600 text-white px-6 py-3 rounded-full font-bold shadow-lg hover:bg-red-700 transition no-tap-fix" style={{ minHeight: 'unset' }}>
                        Browse Restaurants
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 pb-40 lg:pb-0 relative">
            {/* Mobile App Bar */}
            <div className="md:hidden bg-white flex items-center px-4 h-14 border-b border-gray-100 sticky top-0 z-40">
                <button onClick={() => navigate(-1)} className="p-2 -ml-2 text-gray-800">
                    <span className="text-xl leading-none">←</span>
                </button>
                <h1 className="ml-2 text-lg font-black text-gray-900 truncate flex-1">
                    {restaurant?.name || 'Cart'}
                </h1>
            </div>

            <div className="w-full mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
                <h1 className="hidden md:block text-2xl sm:text-3xl font-bold text-gray-900 mb-4 sm:mb-8">Your Cart</h1>

                <div className="flex flex-col lg:flex-row gap-6 lg:gap-8">
                    {/* Cart Items */}
                    <div className="flex-grow">
                        <div className="bg-white rounded-xl shadow-sm overflow-hidden mb-4 sm:mb-6">
                            <div className="p-4 sm:p-6 border-b border-gray-100 flex justify-between items-center">
                                <div className="text-base sm:text-lg font-bold text-gray-800">
                                    Ordering from <span className="text-red-600">{restaurant?.name}</span>
                                </div>
                            </div>

                            <div className="divide-y divide-gray-100">
                                {cartItems.map((item) => (
                                    <div key={item.id} className="p-4 sm:p-6 flex items-center justify-between gap-3">
                                        <div className="flex items-center space-x-3 flex-1 min-w-0">
                                            <span className={`h-4 w-4 rounded-sm border flex-shrink-0 flex items-center justify-center text-[10px] ${item.veg_type === 'VEG' ? 'border-green-600 text-green-600' : 'border-red-600 text-red-600'}`}>●</span>
                                            <div className="min-w-0">
                                                <h3 className="font-medium text-gray-900 leading-tight text-sm sm:text-base truncate">{item.name}</h3>
                                                <p className="text-sm text-gray-500">₹{item.price}</p>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-3 flex-shrink-0">
                                            {/* Quantity Controls — larger tap area on mobile */}
                                            <div className="flex items-center border-2 border-gray-200 rounded-xl overflow-hidden">
                                                <button
                                                    onClick={() => updateQuantity(item.id, -1)}
                                                    className="w-10 h-10 sm:w-11 sm:h-11 text-gray-600 hover:bg-gray-100 font-bold transition-colors flex items-center justify-center text-lg"
                                                    style={{ minHeight: 'unset' }}
                                                >
                                                    −
                                                </button>
                                                <span className="w-8 text-center text-sm font-bold text-gray-900 border-x-2 border-gray-200 h-10 sm:h-11 flex items-center justify-center">
                                                    {item.quantity}
                                                </span>
                                                <button
                                                    onClick={() => updateQuantity(item.id, 1)}
                                                    className="w-10 h-10 sm:w-11 sm:h-11 text-green-600 hover:bg-gray-100 font-bold transition-colors flex items-center justify-center text-lg"
                                                    style={{ minHeight: 'unset' }}
                                                >
                                                    +
                                                </button>
                                            </div>

                                            <div className="text-right font-bold text-gray-900 w-16 text-sm sm:text-base">
                                                ₹{(item.price * item.quantity).toFixed(0)}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Bill Summary — desktop side panel */}
                    <div className="hidden lg:block lg:w-96 flex-shrink-0">
                        <div className="bg-white rounded-xl shadow-sm p-6 sticky top-24">
                            <h2 className="text-lg font-bold text-gray-900 mb-4">Bill Details</h2>
                            <div className="space-y-3 text-sm text-gray-600 mb-6">
                                <div className="flex justify-between"><span>Item Total</span><span>₹{subtotal.toFixed(2)}</span></div>
                                <div className="flex justify-between"><span>Delivery Fee</span><span>₹{deliveryFee.toFixed(2)}</span></div>
                                <div className="flex justify-between"><span>Govt. Taxes & Charges</span><span>₹{taxes.toFixed(2)}</span></div>
                                <div className="border-t border-gray-200 pt-3 flex justify-between font-bold text-gray-900 text-base">
                                    <span>To Pay</span><span>₹{total.toFixed(2)}</span>
                                </div>
                            </div>
                            <button
                                onClick={() => navigate('/client/checkout')}
                                className="w-full bg-green-600 text-white py-4 rounded-xl font-bold shadow-lg hover:bg-green-700 transition duration-200 text-base"
                                style={{ minHeight: 'unset' }}
                            >
                                Proceed to Pay — ₹{total.toFixed(2)}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* ===== MOBILE STICKY BOTTOM CHECKOUT PANEL ===== */}
            <div className="lg:hidden fixed bottom-[60px] md:bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 shadow-[0_-4px_20px_-10px_rgba(0,0,0,0.1)] pb-[env(safe-area-inset-bottom)]">
                {/* Expandable bill summary */}
                {mobileShowSummary && (
                    <div className="px-4 pt-4 pb-2 border-b border-gray-100 space-y-2 text-sm text-gray-700">
                        <div className="flex justify-between"><span>Item Total</span><span>₹{subtotal.toFixed(2)}</span></div>
                        <div className="flex justify-between"><span>Delivery Fee</span><span>₹{deliveryFee.toFixed(2)}</span></div>
                        <div className="flex justify-between"><span>Taxes</span><span>₹{taxes.toFixed(2)}</span></div>
                    </div>
                )}
                <div className="flex items-center gap-3 p-4">
                    {/* Bill toggle */}
                    <button
                        onClick={() => setMobileShowSummary(!mobileShowSummary)}
                        className="flex flex-col items-start min-w-0"
                        style={{ minHeight: 'unset' }}
                    >
                        <span className="text-xs text-gray-500 font-medium">Total</span>
                        <span className="text-lg font-black text-gray-900 flex items-center gap-1">
                            ₹{total.toFixed(2)}
                            <svg className={`w-4 h-4 text-gray-400 transition-transform ${mobileShowSummary ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </span>
                        <span className="text-[10px] text-gray-400 underline">incl. all taxes</span>
                    </button>
                    <button
                        onClick={() => navigate('/client/checkout')}
                        className="flex-1 bg-green-600 text-white py-4 rounded-2xl font-black shadow-lg hover:bg-green-700 transition text-base text-center"
                        style={{ minHeight: 'unset' }}
                    >
                        Proceed to Pay
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Cart;
