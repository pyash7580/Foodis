import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axiosInstance from '../../api/axiosInstance';
import Navbar from '../../components/Navbar';
import { getRestaurantCover } from '../../utils/images';
import { useCart } from '../../contexts/CartContext';
import { useAuth } from '../../contexts/AuthContext';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';

const RestaurantDetails = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { token } = useAuth();
    const [restaurant, setRestaurant] = useState(null);
    const [menuItems, setMenuItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [dietFilter, setDietFilter] = useState('ALL'); // 'ALL', 'VEG', 'NON_VEG'

    // Cart Context
    const { addToCart, cartItems, getCartCount, getCartTotal, updateQuantity } = useCart();

    useEffect(() => {
        if (!id) {
            setError('Invalid restaurant');
            setLoading(false);
            return;
        }

        const fetchAll = async () => {
            setLoading(true);
            setError(null);
            try {
                // Fetch restaurant detail
                const res = await axiosInstance.get(
                    `/api/client/restaurants/${id}/`
                );
                setRestaurant(res.data);

                // Fetch menu separately — failure here won't break page
                try {
                    const menuRes = await axiosInstance.get(
                        `/api/client/restaurants/${id}/menu/`
                    );
                    const items = menuRes.data?.results || menuRes.data;
                    setMenuItems(Array.isArray(items) ? items : []);
                } catch (menuErr) {
                    console.warn('Menu load failed:', menuErr);
                    setMenuItems([]);
                }
            } catch (err) {
                console.error('Restaurant detail error:', err);
                if (err.response?.status === 404) {
                    setError('Restaurant not found');
                } else {
                    setError('Could not load restaurant. Please try again.');
                }
            } finally {
                setLoading(false);
            }
        };

        fetchAll();
    }, [id]);

    const toggleFavItem = async (itemId) => {
        if (!token) {
            toast.error("Please login to favourite items");
            return;
        }
        try {
            const res = await axiosInstance.post('/api/client/favourite-menu-items/toggle/',
                { menu_item_id: itemId },
                { headers: { 'X-Role': 'CLIENT' } }
            );

            setMenuItems(prev => prev.map(item =>
                item.id === itemId ? { ...item, is_favourite: res.data.status === 'added' } : item
            ));

            toast.success(res.data.status === 'added' ? "Added to favourites!" : "Removed from favourites");
        } catch (err) {
            toast.error("Failed to update favorite");
        }
    };

    if (loading) return (
        <div className="flex justify-center items-center min-h-screen">
            <div className="animate-spin h-10 w-10 rounded-full 
                          border-4 border-red-500 border-t-transparent" />
        </div>
    );

    if (error) return (
        <div className="flex flex-col items-center justify-center 
                        min-h-screen gap-4">
            <span className="text-6xl">🍽️</span>
            <p className="text-red-500 text-xl font-semibold">{error}</p>
            <button
                onClick={() => navigate(-1)}
                className="bg-red-500 text-white px-8 py-3 rounded-full 
                       font-semibold hover:bg-red-600 transition-all"
            >
                ← Go Back
            </button>
        </div>
    );
    if (!restaurant) return <div className="p-8 text-center text-red-500 font-bold">🚫 Restaurant not found</div>;

    const coverImage = restaurant.cover_image_url || getRestaurantCover(restaurant.id);

    return (
        <div className="min-h-screen bg-gray-50 pb-20">
            <Navbar />

            {/* Hero Section */}
            <div className="relative h-80 w-full overflow-hidden">
                <div className="absolute inset-0 bg-cover bg-center transition-transform duration-1000 hover:scale-105"
                    style={{ backgroundImage: `url(${coverImage})` }}>
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent"></div>
                </div>

                <div className="absolute bottom-0 left-0 right-0 max-w-[1600px] mx-auto px-4 pb-8 flex flex-col sm:flex-row sm:items-end">
                    {restaurant.image_url ? (
                        <img
                            src={restaurant.image_url}
                            alt={restaurant.name}
                            className="w-full h-64 object-cover rounded-xl"
                            onError={(e) => {
                                e.target.style.display = 'none';
                            }}
                        />
                    ) : (
                        <div className="w-full h-64 bg-gradient-to-br from-orange-50 to-red-100 flex items-center justify-center rounded-xl">
                            <span className="text-7xl">🍽️</span>
                        </div>
                    )}
                    <div className="text-white flex-1 mb-2">
                        <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 mb-2">
                            <h1 className="text-3xl sm:text-5xl font-black leading-tight">{restaurant.name}</h1>
                            <span className="bg-green-600 px-2 py-1 rounded-lg text-sm font-bold shadow-lg flex items-center gap-1">
                                {restaurant.rating} ★
                            </span>
                        </div>
                        <p className="text-lg opacity-90 font-medium">{restaurant.cuisine} • {restaurant.city} • {restaurant.delivery_time} mins</p>
                    </div>
                </div>
            </div>

            <div className="max-w-[1600px] mx-auto px-4 py-8">
                <div className="bg-white rounded-3xl shadow-sm overflow-hidden mb-12 border border-gray-100">
                    <div className="p-8">
                        <h2 className="text-2xl font-black text-gray-900 mb-4">About the Place</h2>
                        <p className="text-gray-600 leading-relaxed font-medium mb-6 text-lg">{restaurant.description}</p>
                        <div className="flex items-center gap-2 text-gray-500">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                            </svg>
                            <span className="font-semibold italic">{restaurant.address}</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center justify-between mb-8">
                    <h2 className="text-3xl font-black text-gray-900">Menu Highlights</h2>

                    {/* VEG/NON-VEG Filter Buttons */}
                    <div className="flex items-center flex-wrap gap-2 sm:gap-3 bg-white border-2 border-gray-200 rounded-2xl p-1.5 shadow-sm mt-4 sm:mt-0">
                        <button
                            onClick={() => setDietFilter('ALL')}
                            className={`px-6 py-2.5 rounded-xl font-bold transition-all duration-300 ${dietFilter === 'ALL'
                                ? 'bg-gray-900 text-white shadow-md'
                                : 'text-gray-600 hover:bg-gray-100'
                                }`}
                        >
                            ALL
                        </button>
                        <button
                            onClick={() => setDietFilter('VEG')}
                            className={`px-6 py-2.5 rounded-xl font-bold transition-all duration-300 flex items-center gap-2 ${dietFilter === 'VEG'
                                ? 'bg-green-600 text-white shadow-md'
                                : 'text-green-600 hover:bg-green-50'
                                }`}
                        >
                            <span className="h-4 w-4 rounded-sm border-2 border-current flex items-center justify-center text-[8px]">●</span>
                            VEG
                        </button>
                        <button
                            onClick={() => setDietFilter('NON_VEG')}
                            className={`px-6 py-2.5 rounded-xl font-bold transition-all duration-300 flex items-center gap-2 ${dietFilter === 'NON_VEG'
                                ? 'bg-red-600 text-white shadow-md'
                                : 'text-red-600 hover:bg-red-50'
                                }`}
                        >
                            <span className="h-4 w-4 rounded-sm border-2 border-current flex items-center justify-center text-[8px]">●</span>
                            NON-VEG
                        </button>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {menuItems
                        .filter(item => {
                            if (dietFilter === 'ALL') return true;
                            return item.veg_type === dietFilter;
                        })
                        .map(item => {
                            const cartItem = cartItems.find(c => c.id === item.id);
                            const quantity = cartItem ? cartItem.quantity : 0;

                            return (
                                <motion.div
                                    key={item.id}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="bg-white p-4 sm:p-6 rounded-3xl shadow-sm border border-gray-100 flex flex-col sm:flex-row justify-between sm:items-center items-start group hover:shadow-xl transition-all duration-300 gap-4 sm:gap-0"
                                >
                                    <div className="flex-1 w-full">
                                        <div className="flex items-center mb-2">
                                            <span className={`h-4 w-4 rounded-sm border-2 mr-3 flex items-center justify-center text-[8px] ${item.veg_type === 'VEG' ? 'border-green-600 text-green-600' : 'border-red-600 text-red-600'}`}>
                                                ●
                                            </span>
                                            <h3 className="font-black text-xl text-gray-900 group-hover:text-red-600 transition-colors">{item.name}</h3>

                                            {/* Dish Favorite Button */}
                                            <button
                                                onClick={() => toggleFavItem(item.id)}
                                                className={`ml-3 p-1.5 rounded-full transition-all duration-300 ${item.is_favourite ? 'text-red-500 scale-110' : 'text-gray-300 hover:text-red-400'
                                                    }`}
                                            >
                                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill={item.is_favourite ? "currentColor" : "none"} stroke="currentColor" strokeWidth={item.is_favourite ? "0" : "2"}>
                                                    <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                                                </svg>
                                            </button>
                                        </div>
                                        <p className="text-gray-500 text-sm mb-4 line-clamp-2 font-medium">{item.description}</p>
                                        <p className="font-black text-2xl text-gray-900">₹{item.price}</p>
                                    </div>

                                    <div className="relative w-full sm:w-auto flex justify-center sm:justify-end sm:ml-6 flex-shrink-0">
                                        <div className="h-40 w-full sm:h-28 sm:w-28 rounded-2xl overflow-hidden shadow-lg border-2 border-gray-100 relative">
                                            {item.image_url ? (
                                                <img
                                                    src={item.image_url}
                                                    alt={item.name}
                                                    className="w-20 h-20 object-cover rounded-lg"
                                                    onError={(e) => { e.target.style.display = 'none'; }}
                                                />
                                            ) : (
                                                <div className="w-20 h-20 bg-orange-50 flex items-center justify-center rounded-lg text-3xl">
                                                    🍜
                                                </div>
                                            )}
                                        </div>

                                        <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 w-28 sm:w-24">
                                            {quantity > 0 ? (
                                                <div className="flex items-center justify-between bg-white border-2 border-red-100 rounded-xl overflow-hidden shadow-xl">
                                                    <button
                                                        className="px-3 py-1.5 text-red-600 font-black hover:bg-red-50 transition-colors"
                                                        onClick={() => updateQuantity(item.id, -1)}
                                                    >-</button>
                                                    <span className="text-sm font-black text-gray-900">{quantity}</span>
                                                    <button
                                                        className="px-3 py-1.5 text-red-600 font-black hover:bg-red-50 transition-colors"
                                                        onClick={() => updateQuantity(item.id, 1)}
                                                    >+</button>
                                                </div>
                                            ) : (
                                                <button
                                                    className="w-full bg-white text-red-600 border-2 border-red-50 px-4 py-2 rounded-xl font-black hover:bg-red-50 hover:border-red-100 transition shadow-lg active:scale-95"
                                                    onClick={() => addToCart(item, restaurant)}
                                                >
                                                    ADD
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                </motion.div>
                            );
                        })}
                </div>
            </div>

            {/* Floating Cart Button */}
            {cartItems.length > 0 && (
                <div className="fixed bottom-6 left-0 w-full px-4 z-50">
                    <Link to="/client/cart">
                        <motion.div
                            initial={{ y: 100 }}
                            animate={{ y: 0 }}
                            className="max-w-2xl mx-auto bg-gray-900 text-white p-5 rounded-2xl shadow-2xl flex justify-between items-center hover:bg-black transition cursor-pointer group"
                        >
                            <div className="flex items-center gap-4">
                                <div className="bg-red-600 p-2 rounded-lg">
                                    <span className="font-black text-lg leading-none">{getCartCount()}</span>
                                </div>
                                <div className="flex flex-col">
                                    <span className="font-black text-lg italic tracking-tight uppercase">Order Summary</span>
                                    <span className="text-xs opacity-70 font-bold tracking-widest uppercase">Total: ₹{getCartTotal().toFixed(2)}</span>
                                </div>
                            </div>
                            <div className="flex items-center font-black text-lg gap-3 uppercase tracking-tighter group-hover:gap-5 transition-all">
                                Checkout <span className="text-2xl mt-1">💨</span>
                            </div>
                        </motion.div>
                    </Link>
                </div>
            )}
        </div>
    );
};
export default RestaurantDetails;
