
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../../contexts/CartContext';
import Navbar from '../../components/Navbar';

const Cart = () => {
    const { cartItems, restaurant, updateQuantity, getCartTotal } = useCart();
    const navigate = useNavigate();

    const subtotal = getCartTotal();
    const deliveryFee = restaurant ? parseFloat(restaurant.delivery_fee) : 0;
    const taxes = subtotal * 0.05; // 5% tax mock
    const total = subtotal + deliveryFee + taxes;

    if (cartItems.length === 0) {
        return (
            <div className="min-h-screen bg-gray-50 flex flex-col">
                <Navbar />
                <div className="flex-grow flex flex-col items-center justify-center p-4">
                    <img src="https://cdni.iconscout.com/illustration/premium/thumb/empty-cart-2130356-1800917.png" alt="Empty Cart" className="w-64 h-64 opacity-50 mb-4" />
                    <h2 className="text-2xl font-bold text-gray-700 mb-2">Your Cart is Empty</h2>
                    <p className="text-gray-500 mb-6">Looks like you haven't added anything to your cart yet.</p>
                    <Link to="/client" className="bg-red-600 text-white px-6 py-3 rounded-full font-bold shadow-lg hover:bg-red-700 transition">
                        Browse Restaurants
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <Navbar />
            <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-8">Your Cart</h1>

                <div className="flex flex-col lg:flex-row gap-8">
                    {/* Cart Items */}
                    <div className="flex-grow">
                        <div className="bg-white rounded-xl shadow-sm overflow-hidden mb-6">
                            <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                                <div className="flex items-center">
                                    {/* Small Restaurant Image */}
                                    <div className="text-lg font-bold text-gray-800">
                                        Ordering from <span className="text-red-600">{restaurant?.name}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="divide-y divide-gray-100">
                                {cartItems.map((item) => (
                                    <div key={item.id} className="p-6 flex items-center justify-between">
                                        <div className="flex items-center space-x-4">
                                            <span className={`h-4 w-4 rounded-sm border flex items-center justify-center text-[10px] ${item.veg_type === 'VEG' ? 'border-green-600 text-green-600' : 'border-red-600 text-red-600'}`}>●</span>
                                            <div>
                                                <h3 className="font-medium text-gray-900">{item.name}</h3>
                                                <p className="text-sm text-gray-500">₹{item.price}</p>
                                            </div>
                                        </div>

                                        <div className="flex items-center border border-gray-300 rounded-lg overflow-hidden">
                                            <button
                                                onClick={() => updateQuantity(item.id, -1)}
                                                className="px-3 py-1 text-gray-600 hover:bg-gray-100 font-bold"
                                            >
                                                -
                                            </button>
                                            <span className="px-3 py-1 text-sm font-medium bg-white">{item.quantity}</span>
                                            <button
                                                onClick={() => updateQuantity(item.id, 1)}
                                                className="px-3 py-1 text-green-600 hover:bg-gray-100 font-bold"
                                            >
                                                +
                                            </button>
                                        </div>

                                        <div className="text-right font-medium text-gray-900 w-20">
                                            ₹{item.price * item.quantity}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Bill Summary */}
                    <div className="lg:w-96 flex-shrink-0">
                        <div className="bg-white rounded-xl shadow-sm p-6 sticky top-24">
                            <h2 className="text-lg font-bold text-gray-900 mb-4">Bill Details</h2>

                            <div className="space-y-3 text-sm text-gray-600 mb-6">
                                <div className="flex justify-between">
                                    <span>Item Total</span>
                                    <span>₹{subtotal.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span>Delivery Fee</span>
                                    <span>₹{deliveryFee.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span>Govt. Taxes & Charges</span>
                                    <span>₹{taxes.toFixed(2)}</span>
                                </div>
                                <div className="border-t border-gray-200 pt-3 flex justify-between font-bold text-gray-900 text-base">
                                    <span>To Pay</span>
                                    <span>₹{total.toFixed(2)}</span>
                                </div>
                            </div>

                            <button
                                onClick={() => navigate('/client/checkout')}
                                className="w-full bg-green-600 text-white py-3 rounded-lg font-bold shadow-lg hover:bg-green-700 transition duration-200"
                            >
                                Proceed to Pay
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Cart;
