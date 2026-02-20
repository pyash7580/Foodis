import { API_BASE_URL } from '../../config';

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Navbar from '../../components/Navbar';
import { useCart } from '../../contexts/CartContext';
import { useAuth } from '../../contexts/AuthContext';
import toast from 'react-hot-toast';
import PaymentProcessModal from '../../components/PaymentProcessModal';
import PaymentQRModal from '../../components/PaymentQRModal';

const Checkout = () => {
    const { cartItems, restaurant, getCartTotal, clearCart } = useCart();
    const { user } = useAuth();
    const navigate = useNavigate();

    // UI State
    const [step, setStep] = useState(1); // 1: Cart, 2: Address, 3: Payment
    const [loading, setLoading] = useState(false);
    const [processStatus, setProcessStatus] = useState({ isOpen: false, status: '', message: '' });

    // Data State
    const [addresses, setAddresses] = useState([]);
    const [selectedAddress, setSelectedAddress] = useState(null);
    const [isAddingAddress, setIsAddingAddress] = useState(false);
    const [newAddress, setNewAddress] = useState({
        label: 'Home',
        address_line1: '',
        city: '',
        state: '',
        pincode: '',
        latitude: 12.9716, // Default Bangalore
        longitude: 77.5946
    });

    const [razorpayKey, setRazorpayKey] = useState('');
    const [walletBalance, setWalletBalance] = useState(0);
    const [savedPayments, setSavedPayments] = useState([]);
    const [selectedSavedId, setSelectedSavedId] = useState(null);

    // Selection State
    const [paymentMethod, setPaymentMethod] = useState('UPI');
    const [useWallet, setUseWallet] = useState(false);
    const [couponCode, setCouponCode] = useState('');
    const [discount, setDiscount] = useState(0);

    // Card Details state
    const [cardDetails, setCardDetails] = useState({
        name: '',
        number: '',
        expiry: '',
        cvv: ''
    });
    const [showQRModal, setShowQRModal] = useState(false);
    const [pendingOrderId, setPendingOrderId] = useState(null);

    // Totals Calculation
    const subtotal = getCartTotal();
    const deliveryFee = restaurant ? parseFloat(restaurant.delivery_fee) : 0;
    const platformFee = 5.00;

    // Zomato-like Tax Logic (5% on food, 18% on fees)
    const foodTax = subtotal * 0.05;
    const feeTax = (deliveryFee + platformFee) * 0.18;
    const totalTax = foodTax + feeTax;

    const grossTotal = subtotal + deliveryFee + platformFee + totalTax;
    const finalTotal = Math.max(0, grossTotal - discount);

    // Wallet Logic
    const walletContribution = useWallet ? Math.min(walletBalance, finalTotal) : 0;
    const onlinePayable = finalTotal - walletContribution;

    useEffect(() => {
        if (!user) {
            navigate('/login');
            return;
        }

        const fetchData = async () => {
            try {
                // 1. Config & Wallet
                const configRes = await axios.get(`${API_BASE_URL}/api/auth/config/`);
                setRazorpayKey(configRes.data.razorpay_key || 'rzp_test_demo_12345');

                const walletRes = await axios.get(`${API_BASE_URL}/api/client/wallet/`);
                const bal = Array.isArray(walletRes.data) && walletRes.data.length > 0
                    ? walletRes.data[0].balance
                    : (walletRes.data.balance || 0);
                setWalletBalance(parseFloat(bal));

                // 2. Addresses
                const addrRes = await axios.get(`${API_BASE_URL}/api/auth/addresses/`);
                const addressesData = addrRes.data.results || (Array.isArray(addrRes.data) ? addrRes.data : []);
                setAddresses(addressesData);
                if (addressesData.length > 0) {
                    setSelectedAddress(addressesData.find(a => a.is_default) || addressesData[0]);
                }

                // 3. Saved Payments
                const payRes = await axios.get(`${API_BASE_URL}/api/client/saved-payments/`);
                const paymentsData = payRes.data.results || (Array.isArray(payRes.data) ? payRes.data : []);
                setSavedPayments(paymentsData);
            } catch (err) {
                console.error("Fetch error", err);
            }
        };

        fetchData();

        // Load Razorpay
        const script = document.createElement('script');
        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
        script.async = true;
        document.body.appendChild(script);

        return () => {
            if (document.body.contains(script)) {
                document.body.removeChild(script);
            }
        };
    }, [user, navigate]);

    const handleAddAddress = async (e) => {
        e.preventDefault();
        try {
            const res = await axios.post(`${API_BASE_URL}/api/client/addresses/`, newAddress);
            setAddresses([...addresses, res.data]);
            setSelectedAddress(res.data);
            setIsAddingAddress(false);
            setNewAddress({
                label: 'Home',
                address_line1: '',
                city: '',
                state: '',
                pincode: '',
                latitude: 12.9716,
                longitude: 77.5946
            });
            toast.success("Address added successfully!");
        } catch (err) {
            toast.error("Failed to add address. Check fields.");
        }
    };

    const handlePlaceOrder = async () => {
        if (!selectedAddress) {
            toast.error("Please select a delivery address");
            setStep(2);
            return;
        }

        setLoading(true);
        setProcessStatus({ isOpen: true, status: 'initiating', message: 'Securing your order...' });

        try {
            // Synchronize local cart with server before placing order
            const syncRes = await axios.post(`${API_BASE_URL}/api/client/cart/sync/`, {
                restaurant_id: restaurant.id,
                items: cartItems
            });
            const backendCart = syncRes.data;

            if (!backendCart || !backendCart.items || backendCart.items.length === 0) {
                toast.error("Cart synchronization failed. Please try again.");
                return;
            }

            // Create Order
            const response = await axios.post(`${API_BASE_URL}/api/client/orders/`, {
                cart_id: backendCart.id,
                address_id: selectedAddress.id,
                payment_method: paymentMethod,
                use_wallet: useWallet,
                coupon_code: couponCode
            });

            const order = response.data;
            setPendingOrderId(order.order_id);

            // Handle Full Wallet or COD
            if (order.online_amount === 0 || paymentMethod === 'COD') {
                setProcessStatus({ isOpen: true, status: 'verifying', message: 'Confirming order...' });
                setTimeout(() => {
                    clearCart();
                    navigate(`/payment-success/${order.order_id}`);
                    setProcessStatus({ isOpen: false, status: '', message: '' });
                }, 1500);
                return;
            }

            // UPI Flow - Show QR Modal
            if (paymentMethod === 'UPI') {
                setLoading(false);
                setProcessStatus({ isOpen: false, status: '', message: '' });
                setShowQRModal(true);
                return;
            }

            // Razorpay Flow
            setProcessStatus({ isOpen: true, status: 'processing', message: 'Connecting to Bank...' });

            const isDemoMode = razorpayKey.includes('demo') || (order.razorpay_order_id && order.razorpay_order_id.startsWith('demo_'));

            if (isDemoMode) {
                // For CARD payment in demo mode, we simulate a slight delay
                const delay = paymentMethod === 'CARD' ? 3000 : 2000;
                setProcessStatus({
                    isOpen: true,
                    status: 'processing',
                    message: paymentMethod === 'CARD' ? 'Verifying Card with Bank...' : 'Connecting to Bank...'
                });

                setTimeout(async () => {
                    await axios.post(`${API_BASE_URL}/api/client/orders/${order.order_id}/simulate_payment/`);
                    clearCart();
                    navigate(`/payment-success/${order.order_id}`);
                    setProcessStatus({ isOpen: false, status: '', message: '' });
                }, delay);
                return;
            }

            const options = {
                key: razorpayKey,
                amount: order.online_amount * 100,
                currency: "INR",
                name: "Foodis",
                description: `Order #${order.order_id}`,
                order_id: order.razorpay_order_id,
                handler: async function (rzpRes) {
                    setProcessStatus({ isOpen: true, status: 'verifying', message: 'Verifying payment...' });
                    try {
                        await axios.post(`${API_BASE_URL}/api/client/orders/${order.order_id}/verify_payment/`, {
                            razorpay_payment_id: rzpRes.razorpay_payment_id,
                            razorpay_order_id: rzpRes.razorpay_order_id,
                            razorpay_signature: rzpRes.razorpay_signature
                        });
                        clearCart();
                        navigate(`/payment-success/${order.order_id}`);
                    } catch (err) {
                        toast.error("Payment verification failed. Contact support.");
                    }
                    setProcessStatus({ isOpen: false, status: '', message: '' });
                },
                prefill: {
                    name: user.name,
                    email: user.email || '',
                    contact: user.phone
                },
                theme: { color: "#dc2626" },
                modal: {
                    ondismiss: function () {
                        setLoading(false);
                        setProcessStatus({ isOpen: false, status: '', message: '' });
                    }
                }
            };

            const rzp = new window.Razorpay(options);
            rzp.on('payment.failed', function (res) {
                toast.error(res.error.description);
                setLoading(false);
                setProcessStatus({ isOpen: false, status: '', message: '' });
            });
            rzp.open();

        } catch (error) {
            console.error("Checkout error", error);
            const msg = error.response?.data?.error || "Order failed. Try again.";
            toast.error(msg);
            setLoading(false);
            setProcessStatus({ isOpen: false, status: '', message: '' });
        }
    };

    if (cartItems.length === 0) {
        navigate('/client/cart');
        return null;
    }

    return (
        <div className="min-h-screen bg-gray-50 pb-24">
            <Navbar />
            <PaymentProcessModal {...processStatus} />

            <div className="max-w-xl mx-auto px-4 py-8">
                {/* Step Indicator */}
                <div className="flex items-center justify-between mb-8 px-2">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="flex items-center flex-1 last:flex-none">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm transition-all shadow-sm ${step >= i ? 'bg-red-600 text-white' : 'bg-gray-200 text-gray-400'}`}>
                                {step > i ? '✓' : i}
                            </div>
                            {i < 3 && <div className={`h-1 flex-1 mx-2 rounded ${step > i ? 'bg-red-600' : 'bg-gray-200'}`}></div>}
                        </div>
                    ))}
                </div>

                {/* Step 1: Cart Review */}
                {step === 1 && (
                    <div className="animate-in slide-in-from-right-4 duration-300">
                        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden mb-6">
                            <div className="p-6 bg-red-50 border-b border-red-100">
                                <h1 className="text-xl font-black text-gray-900">Review your order</h1>
                                <p className="text-sm text-gray-500 font-medium">{restaurant?.name}</p>
                            </div>

                            <div className="p-6 space-y-4">
                                {cartItems.map(item => (
                                    <div key={item.id} className="flex justify-between items-start">
                                        <div className="flex space-x-3">
                                            <div className="w-5 h-5 border-2 border-gray-300 rounded flex items-center justify-center p-0.5 mt-0.5">
                                                <div className={`w-full h-full rounded-full ${item.is_veg ? 'bg-green-600' : 'bg-red-600'}`}></div>
                                            </div>
                                            <div>
                                                <p className="font-bold text-gray-900 leading-tight">{item.name}</p>
                                                <p className="text-xs text-gray-400 font-bold mt-1">₹{item.price} x {item.quantity}</p>
                                            </div>
                                        </div>
                                        <p className="font-bold text-gray-900">₹{item.price * item.quantity}</p>
                                    </div>
                                ))}
                            </div>

                            <div className="p-6 bg-gray-50 border-t border-gray-100 space-y-3">
                                <div className="flex justify-between text-sm font-medium text-gray-600">
                                    <span>Item Total</span>
                                    <span>₹{subtotal.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between text-sm font-medium text-gray-600">
                                    <span>Delivery Fee</span>
                                    <span>₹{deliveryFee.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between text-sm font-medium text-gray-600">
                                    <span>Platform Fee</span>
                                    <span>₹{platformFee.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between text-sm font-medium text-gray-400">
                                    <span className="flex items-center">
                                        GST & Taxes <span className="ml-1 text-[10px] border px-1 rounded">INFO</span>
                                    </span>
                                    <span>₹{totalTax.toFixed(2)}</span>
                                </div>
                                {discount > 0 && (
                                    <div className="flex justify-between text-sm font-bold text-green-600">
                                        <span>Coupon Discount</span>
                                        <span>- ₹{discount.toFixed(2)}</span>
                                    </div>
                                )}
                                <div className="pt-3 border-t border-gray-200 flex justify-between items-center">
                                    <span className="text-lg font-black text-gray-900">Total</span>
                                    <span className="text-xl font-black text-gray-900">₹{finalTotal.toFixed(2)}</span>
                                </div>
                            </div>
                        </div>

                        <button
                            onClick={() => setStep(2)}
                            className="w-full bg-red-600 text-white py-4 rounded-2xl font-black text-lg shadow-xl hover:bg-red-700 transition active:scale-95 flex items-center justify-center group"
                        >
                            Next: Delivery Address
                            <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
                        </button>
                    </div>
                )}

                {/* Step 2: Address Selection */}
                {step === 2 && (
                    <div className="animate-in slide-in-from-right-4 duration-300">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-2xl font-black text-gray-900">Delivery at</h2>
                            {!isAddingAddress && (
                                <button
                                    onClick={() => setIsAddingAddress(true)}
                                    className="text-red-600 font-bold text-sm bg-red-50 px-4 py-2 rounded-full hover:bg-red-100 transition"
                                >
                                    + Add New
                                </button>
                            )}
                        </div>

                        {isAddingAddress ? (
                            <form onSubmit={handleAddAddress} className="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm mb-8 space-y-4">
                                <h3 className="font-black text-gray-900 mb-2">New Address Details</h3>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm font-bold text-gray-400 uppercase tracking-widest sm:pl-2 mt-6 sm:mt-8 mb-2">
                                    <div className="sm:col-span-2">
                                        <label className="block mb-1 text-[10px]">Label (e.g. Home, Work)</label>
                                        <input
                                            type="text"
                                            required
                                            className="w-full p-3 rounded-xl border border-gray-200 text-gray-900 focus:border-red-500 outline-none"
                                            value={newAddress.label}
                                            onChange={(e) => setNewAddress({ ...newAddress, label: e.target.value })}
                                        />
                                    </div>
                                    <div className="sm:col-span-2">
                                        <label className="block mb-1 text-[10px]">Address Line 1</label>
                                        <input
                                            type="text"
                                            required
                                            className="w-full p-3 rounded-xl border border-gray-200 text-gray-900 focus:border-red-500 outline-none"
                                            value={newAddress.address_line1}
                                            onChange={(e) => setNewAddress({ ...newAddress, address_line1: e.target.value })}
                                        />
                                    </div>
                                    <div className="sm:col-span-2">
                                        <label className="block mb-1 text-[10px]">City</label>
                                        <input
                                            type="text"
                                            required
                                            className="w-full p-3 rounded-xl border border-gray-200 text-gray-900 focus:border-red-500 outline-none"
                                            value={newAddress.city}
                                            onChange={(e) => setNewAddress({ ...newAddress, city: e.target.value })}
                                        />
                                    </div>
                                    <div>
                                        <label className="block mb-1 text-[10px]">State</label>
                                        <input
                                            type="text"
                                            required
                                            className="w-full p-3 rounded-xl border border-gray-200 text-gray-900 focus:border-red-500 outline-none"
                                            value={newAddress.state}
                                            onChange={(e) => setNewAddress({ ...newAddress, state: e.target.value })}
                                        />
                                    </div>
                                    <div>
                                        <label className="block mb-1 text-[10px]">Pincode</label>
                                        <input
                                            type="text"
                                            required
                                            className="w-full p-3 rounded-xl border border-gray-200 text-gray-900 focus:border-red-500 outline-none"
                                            value={newAddress.pincode}
                                            onChange={(e) => setNewAddress({ ...newAddress, pincode: e.target.value })}
                                        />
                                    </div>
                                </div>
                                <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3 mt-6">
                                    <button
                                        type="button"
                                        onClick={() => setIsAddingAddress(false)}
                                        className="flex-1 py-3 rounded-xl border border-gray-200 font-bold text-gray-500 hover:bg-gray-50"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        className="flex-1 py-3 rounded-xl bg-red-600 text-white font-bold hover:bg-red-700 shadow-lg"
                                    >
                                        Save Address
                                    </button>
                                </div>
                            </form>
                        ) : (
                            <div className="space-y-4 mb-8">
                                {addresses.length === 0 ? (
                                    <div className="p-12 text-center bg-gray-50 rounded-3xl border-2 border-dashed border-gray-200 text-gray-400 font-bold">
                                        No addresses saved. Please add one.
                                    </div>
                                ) : (
                                    Array.isArray(addresses) && addresses.map(addr => (
                                        <div
                                            key={addr.id}
                                            onClick={() => setSelectedAddress(addr)}
                                            className={`p-5 rounded-3xl border-2 cursor-pointer transition-all ${selectedAddress?.id === addr.id ? 'border-red-600 bg-red-50' : 'border-white bg-white hover:border-gray-200'}`}
                                        >
                                            <div className="flex items-start">
                                                <span className="text-2xl mr-4 hidden sm:block">{addr.label === 'Home' ? '🏠' : addr.label === 'Work' ? '💼' : '📍'}</span>
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <span className="text-xl sm:hidden">{addr.label === 'Home' ? '🏠' : addr.label === 'Work' ? '💼' : '📍'}</span>
                                                        <p className="font-black text-gray-900 text-lg uppercase tracking-tight m-0 leading-none">{addr.label}</p>
                                                    </div>
                                                    <p className="text-sm text-gray-500 font-medium leading-snug mt-1">
                                                        {addr.address_line1}, {addr.city}, {addr.state} - {addr.pincode}
                                                    </p>
                                                    {selectedAddress?.id === addr.id && (
                                                        <div className="mt-4 flex items-center text-red-600 text-xs font-bold bg-white w-fit px-3 py-1.5 rounded-full border border-red-100">
                                                            <span className="w-2 h-2 bg-red-600 rounded-full mr-2 animate-pulse"></span>
                                                            DELIVERING TO THIS ADDRESS
                                                        </div>
                                                    )}
                                                </div>
                                                <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${selectedAddress?.id === addr.id ? 'border-red-600' : 'border-gray-300'}`}>
                                                    {selectedAddress?.id === addr.id && <div className="w-3 h-3 bg-red-600 rounded-full"></div>}
                                                </div>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        )}

                        <div className="flex space-x-4">
                            <button onClick={() => setStep(1)} className="flex-1 bg-gray-200 text-gray-700 py-4 rounded-2xl font-black transition hover:bg-gray-300">Back</button>
                            <button
                                onClick={() => setStep(3)}
                                disabled={!selectedAddress || isAddingAddress}
                                className={`flex-[2] py-4 rounded-2xl font-black text-lg shadow-xl transition active:scale-95 ${!selectedAddress || isAddingAddress ? 'bg-gray-300 text-gray-500 cursor-not-allowed shadow-none' : 'bg-red-600 text-white shadow-red-200'}`}
                            >
                                Next: Payment
                            </button>
                        </div>
                    </div>
                )}

                {/* Step 3: Payment Selection */}
                {step === 3 && (
                    <div className="animate-in slide-in-from-right-4 duration-300">
                        <h2 className="text-2xl font-black text-gray-900 mb-6">Select Payment</h2>

                        {/* Order Summary Summary */}
                        <div className="bg-red-600 rounded-3xl p-6 text-white mb-8 shadow-xl shadow-red-100 flex justify-between items-center overflow-hidden relative">
                            <div className="absolute top-0 right-0 w-32 h-32 bg-white opacity-5 rounded-full -mr-16 -mt-16"></div>
                            <div>
                                <p className="text-red-100 text-xs font-black uppercase tracking-widest mb-1">Total Payable</p>
                                <p className="text-3xl font-black">₹{finalTotal.toFixed(2)}</p>
                            </div>
                            <div className="text-right">
                                <p className="text-xs font-medium opacity-80 uppercase leading-none">Delivering to</p>
                                <p className="font-bold mt-1">{selectedAddress?.label}</p>
                            </div>
                        </div>

                        <div className="space-y-4">
                            {/* Wallet Option */}
                            <div className={`p-5 rounded-3xl border-2 transition-all ${useWallet ? 'border-red-600 bg-red-50' : 'border-white bg-white'}`}>
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center">
                                        <div className="w-12 h-12 bg-orange-100 rounded-2xl flex items-center justify-center mr-4">
                                            <span className="text-2xl">💰</span>
                                        </div>
                                        <div>
                                            <p className="font-black text-gray-900">Foodis Wallet</p>
                                            <p className="text-xs text-gray-500 font-bold">Balance: ₹{walletBalance}</p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => setUseWallet(!useWallet)}
                                        className={`w-14 h-8 rounded-full transition-all relative ${useWallet ? 'bg-red-600' : 'bg-gray-300'}`}
                                    >
                                        <div className={`absolute top-1 w-6 h-6 bg-white rounded-full transition-all shadow-md ${useWallet ? 'left-7' : 'left-1'}`}></div>
                                    </button>
                                </div>
                                {useWallet && (
                                    <div className="mt-4 pt-4 border-t border-red-100 flex justify-between items-center">
                                        <p className="text-xs font-bold text-red-600 lowercase tracking-tight">Using ₹{walletContribution} from wallet</p>
                                        <p className="text-xs font-bold text-gray-400">Remaining: ₹{onlinePayable.toFixed(2)}</p>
                                    </div>
                                )}
                            </div>

                            {onlinePayable > 0 && (
                                <>
                                    <h3 className="text-xs font-black text-gray-400 uppercase tracking-widest pl-2 mt-8 mb-2">Pay Remaining via</h3>

                                    {/* UPI */}
                                    <div
                                        onClick={() => setPaymentMethod('UPI')}
                                        className={`p-5 rounded-3xl border-2 cursor-pointer transition-all ${paymentMethod === 'UPI' ? 'border-red-600 bg-red-50' : 'border-white bg-white hover:border-gray-200'}`}
                                    >
                                        <div className="flex items-center">
                                            <div className="w-12 h-12 bg-blue-50 rounded-2xl flex items-center justify-center mr-4">
                                                <img src="https://upload.wikimedia.org/wikipedia/commons/e/e1/UPI-Logo-vector.svg" className="h-4" alt="UPI" />
                                            </div>
                                            <div className="flex-1">
                                                <p className="font-black text-gray-900">UPI</p>
                                                <div className="flex space-x-2 mt-1 opacity-60">
                                                    <span className="text-[10px] bg-white border px-1.5 py-0.5 rounded font-bold">GPAY</span>
                                                    <span className="text-[10px] bg-white border px-1.5 py-0.5 rounded font-bold">PHONEPE</span>
                                                    <span className="text-[10px] bg-white border px-1.5 py-0.5 rounded font-bold">PAYTM</span>
                                                </div>
                                            </div>
                                            <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${paymentMethod === 'UPI' ? 'border-red-600' : 'border-gray-300'}`}>
                                                {paymentMethod === 'UPI' && <div className="w-3 h-3 bg-red-600 rounded-full"></div>}
                                            </div>
                                        </div>

                                        {/* Stored UPI IDs */}
                                        {paymentMethod === 'UPI' && savedPayments.filter(p => p.method_type === 'UPI').length > 0 && (
                                            <div className="mt-4 pt-4 border-t border-blue-100 flex flex-wrap gap-2">
                                                {savedPayments.filter(p => p.method_type === 'UPI').map(upi => (
                                                    <button
                                                        key={upi.id}
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            toast.success(`Using ${upi.upi_id}`);
                                                        }}
                                                        className="px-4 py-2 bg-white border border-blue-200 rounded-xl text-blue-600 font-bold text-xs hover:bg-blue-50 transition"
                                                    >
                                                        {upi.upi_id}
                                                    </button>
                                                ))}
                                            </div>
                                        )}
                                    </div>

                                    {/* CARDS */}
                                    <div
                                        onClick={() => setPaymentMethod('CARD')}
                                        className={`p-5 rounded-3xl border-2 cursor-pointer transition-all ${paymentMethod === 'CARD' ? 'border-red-600 bg-red-50' : 'border-white bg-white hover:border-gray-200'}`}
                                    >
                                        <div className="flex items-start sm:items-center">
                                            <div className="w-12 h-12 bg-purple-50 rounded-2xl flex items-center justify-center mr-4 flex-shrink-0">
                                                <span className="text-2xl">💳</span>
                                            </div>
                                            <div className="flex-1">
                                                <p className="font-black text-gray-900">Debit / Credit Cards</p>
                                                <p className="text-xs text-gray-400 font-bold">Visa, Mastercard, RuPay</p>
                                            </div>
                                            <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${paymentMethod === 'CARD' ? 'border-red-600' : 'border-gray-300'}`}>
                                                {paymentMethod === 'CARD' && <div className="w-3 h-3 bg-red-600 rounded-full"></div>}
                                            </div>
                                        </div>

                                        {/* Inline Card Form */}
                                        {paymentMethod === 'CARD' && (
                                            <div className="mt-6 pt-6 border-t border-gray-100 animate-in slide-in-from-top-2 duration-300">
                                                {/* Saved Cards Picker */}
                                                {savedPayments.filter(p => p.method_type === 'CARD').length > 0 && (
                                                    <div className="mb-6 space-y-2">
                                                        <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2 ml-1">Use Saved Card</label>
                                                        <div className="flex space-x-2 overflow-x-auto pb-2 scrollbar-hide">
                                                            {savedPayments.filter(p => p.method_type === 'CARD').map(card => (
                                                                <button
                                                                    key={card.id}
                                                                    onClick={(e) => {
                                                                        e.stopPropagation();
                                                                        setSelectedSavedId(card.id);
                                                                        setCardDetails({
                                                                            name: user.name,
                                                                            number: `XXXX XXXX XXXX ${card.card_last4}`,
                                                                            expiry: card.card_expiry.split('/')[0] + '/' + card.card_expiry.slice(-2),
                                                                            cvv: ''
                                                                        });
                                                                        toast.success("Card details filled!");
                                                                    }}
                                                                    className={`flex-none px-4 py-2 rounded-xl border-2 transition-all whitespace-nowrap text-sm font-bold ${selectedSavedId === card.id ? 'border-red-600 bg-red-50 text-red-600' : 'border-gray-100 bg-gray-50 text-gray-400'}`}
                                                                >
                                                                    {card.card_brand} •••• {card.card_last4}
                                                                </button>
                                                            ))}
                                                            <button
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    setSelectedSavedId(null);
                                                                    setCardDetails({ name: '', number: '', expiry: '', cvv: '' });
                                                                }}
                                                                className={`flex-none px-4 py-2 rounded-xl border-2 transition-all whitespace-nowrap text-sm font-bold ${!selectedSavedId ? 'border-red-600 bg-red-50 text-red-600' : 'border-gray-100 bg-gray-50 text-gray-400'}`}
                                                            >
                                                                + New Card
                                                            </button>
                                                        </div>
                                                    </div>
                                                )}

                                                <div className="space-y-4">
                                                    <div>
                                                        <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1.5 ml-1">Cardholder Name</label>
                                                        <input
                                                            type="text"
                                                            placeholder="AS RECORDED ON CARD"
                                                            className="w-full p-4 rounded-2xl bg-white border border-gray-200 text-gray-900 font-bold text-sm focus:border-red-500 outline-none transition"
                                                            value={cardDetails.name}
                                                            onChange={(e) => {
                                                                setSelectedSavedId(null);
                                                                setCardDetails({ ...cardDetails, name: e.target.value.toUpperCase() });
                                                            }}
                                                            onClick={(e) => e.stopPropagation()}
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1.5 ml-1">Account / Card Number</label>
                                                        <input
                                                            type="text"
                                                            placeholder="XXXX XXXX XXXX XXXX"
                                                            maxLength="19"
                                                            className="w-full p-4 rounded-2xl bg-white border border-gray-200 text-gray-900 font-bold text-sm focus:border-red-500 outline-none transition"
                                                            value={cardDetails.number}
                                                            onChange={(e) => {
                                                                setSelectedSavedId(null);
                                                                setCardDetails({ ...cardDetails, number: e.target.value.replace(/\s?/g, '').replace(/(\d{4})/g, '$1 ').trim() });
                                                            }}
                                                            onClick={(e) => e.stopPropagation()}
                                                        />
                                                    </div>
                                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                                        <div>
                                                            <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1.5 ml-1">Valid Thru</label>
                                                            <input
                                                                type="text"
                                                                placeholder="MM/YY"
                                                                maxLength="5"
                                                                className="w-full p-4 rounded-2xl bg-white border border-gray-200 text-gray-900 font-bold text-sm focus:border-red-500 outline-none transition"
                                                                value={cardDetails.expiry}
                                                                onChange={(e) => {
                                                                    setSelectedSavedId(null);
                                                                    setCardDetails({ ...cardDetails, expiry: e.target.value });
                                                                }}
                                                                onClick={(e) => e.stopPropagation()}
                                                            />
                                                        </div>
                                                        <div>
                                                            <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1.5 ml-1">CVV</label>
                                                            <input
                                                                type="password"
                                                                placeholder="***"
                                                                maxLength="3"
                                                                className="w-full p-4 rounded-2xl bg-white border border-gray-200 text-gray-900 font-bold text-sm focus:border-red-500 outline-none transition"
                                                                value={cardDetails.cvv}
                                                                onChange={(e) => {
                                                                    setCardDetails({ ...cardDetails, cvv: e.target.value });
                                                                }}
                                                                onClick={(e) => e.stopPropagation()}
                                                                autoFocus={!!selectedSavedId}
                                                            />
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    {/* COD */}
                                    <div
                                        onClick={() => setPaymentMethod('COD')}
                                        className={`p-5 rounded-3xl border-2 cursor-pointer transition-all ${paymentMethod === 'COD' ? 'border-red-600 bg-red-50' : 'border-white bg-white hover:border-gray-200'}`}
                                    >
                                        <div className="flex items-center">
                                            <div className="w-12 h-12 bg-green-50 rounded-2xl flex items-center justify-center mr-4">
                                                <span className="text-2xl">💵</span>
                                            </div>
                                            <div className="flex-1">
                                                <p className="font-black text-gray-900">Cash on Delivery</p>
                                                <p className="text-xs text-gray-400 font-bold">Pay cash to delivery partner</p>
                                            </div>
                                            <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${paymentMethod === 'COD' ? 'border-red-600' : 'border-gray-300'}`}>
                                                {paymentMethod === 'COD' && <div className="w-3 h-3 bg-red-600 rounded-full"></div>}
                                            </div>
                                        </div>
                                    </div>
                                </>
                            )}
                        </div>

                        <div className="flex space-x-4 mt-8">
                            <button onClick={() => setStep(2)} className="flex-1 bg-gray-200 text-gray-700 py-5 rounded-3xl font-black">Back</button>
                            <button
                                onClick={handlePlaceOrder}
                                disabled={loading}
                                className="flex-[2] bg-red-600 text-white py-5 rounded-3xl font-black text-xl shadow-2xl shadow-red-200 flex items-center justify-center relative overflow-hidden group"
                            >
                                <span className={loading ? 'opacity-0' : 'opacity-100'}>PLACE ORDER</span>
                                {loading && (
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <div className="w-6 h-6 border-4 border-white border-t-transparent rounded-full animate-spin"></div>
                                    </div>
                                )}
                            </button>
                        </div>
                    </div>
                )}

                <PaymentProcessModal
                    isOpen={processStatus.isOpen}
                    status={processStatus.status}
                    message={processStatus.message}
                />

                {showQRModal && (
                    <PaymentQRModal
                        amount={onlinePayable}
                        orderId={pendingOrderId}
                        onSuccess={() => {
                            setShowQRModal(false);
                            setProcessStatus({ isOpen: true, status: 'verifying', message: 'Payment Confirmed! Finalizing...' });
                            setTimeout(() => {
                                clearCart();
                                navigate(`/payment-success/${pendingOrderId}`);
                            }, 1500);
                        }}
                        onClose={() => {
                            setShowQRModal(false);
                            setLoading(false);
                        }}
                    />
                )}
            </div>
        </div>
    );
};

export default Checkout;
