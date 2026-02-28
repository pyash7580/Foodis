import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axiosInstance from '../../api/axiosInstance';
import Navbar from '../../components/Navbar';
import { getRestaurantCover, getRestaurantImage } from '../../utils/images';
import { getMediaImageUrl } from '../../utils/mediaImageUrl';
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

    const coverImage = getMediaImageUrl(restaurant.cover_image_url) || getRestaurantCover(restaurant.id);

    return (
        <div className="min-h-screen bg-gray-50 pb-20">
            <Navbar />

            {/* Compact Hero Section */}
            <div className="relative h-64 w-full overflow-hidden">
                <div className="absolute inset-0 bg-cover bg-center transition-transform duration-1000 hover:scale-105"
                    style={{ backgroundImage: `url(${coverImage})` }}>
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
                </div>

                <div className="absolute inset-0 flex items-end">
                    <div className="max-w-[1400px] w-full mx-auto px-6 pb-4 flex items-center gap-6">
                        {/* Restaurant Logo/Thumbnail */}
                        <div className="relative hidden sm:block">
                            <div className="w-28 h-28 rounded-2xl overflow-hidden border-4 border-white shadow-xl bg-white">
                                <img
                                    src={getMediaImageUrl(restaurant.image_url) || getRestaurantImage(restaurant.id)}
                                    alt={restaurant.name}
                                    className="w-full h-full object-cover"
                                    onError={(e) => {
                                        const fallback = getRestaurantImage(restaurant.id);
                                        if (e.target.src !== fallback) e.target.src = fallback;
                                    }}
                                />
                            </div>
                        </div>

                        <div className="text-white flex-1 drop-shadow-md">
                            <div className="flex items-center gap-3 mb-0.5">
                                <h1 className="text-3xl sm:text-4xl font-black">{restaurant.name}</h1>
                                <span className="bg-green-600 px-2 py-0.5 rounded-lg text-xs font-bold shadow-lg flex items-center gap-1">
                                    {restaurant.rating} ★
                                </span>
                            </div>
                            <p className="text-sm sm:text-base opacity-90 font-semibold tracking-wide">
                                {restaurant.cuisine} • {restaurant.city} • {restaurant.delivery_time} mins
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-[1400px] mx-auto px-6 py-4">
                {/* About Section - Super Compact */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 mb-6">
                    <h2 className="text-lg font-black text-gray-900 mb-1">About the Place</h2>
                    <p className="text-gray-500 leading-tight font-medium mb-3 text-sm italic">{restaurant.description}</p>
                    <div className="flex items-center gap-2 text-gray-400 text-xs">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                        </svg>
                        <span className="font-bold">{restaurant.address}</span>
                    </div>
                </div>

                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
                    <h2 className="text-xl font-black text-gray-900 tracking-tight">Menu Highlights</h2>

                    {/* Compact Filter Buttons */}
                    <div className="flex items-center gap-1 bg-gray-100 p-1 rounded-xl">
                        {['ALL', 'VEG', 'NON_VEG'].map(filter => (
                            <button
                                key={filter}
                                onClick={() => setDietFilter(filter)}
                                className={`px-4 py-1.5 rounded-lg text-[10px] font-black transition-all duration-200 ${dietFilter === filter
                                    ? (filter === 'VEG' ? 'bg-green-600 text-white' : filter === 'NON_VEG' ? 'bg-red-600 text-white' : 'bg-gray-900 text-white')
                                    : 'text-gray-500 hover:text-gray-900'
                                    }`}
                            >
                                {filter.replace('_', '-')}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Grid - Refined Spacing */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
                                    initial={{ opacity: 0, y: 15 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-between group hover:shadow-md transition-all duration-300 gap-4"
                                >
                                    <div className="flex-1">
                                        <div className="flex items-center mb-1">
                                            <span className={`h-3 w-3 rounded-sm border-2 mr-2 flex items-center justify-center text-[6px] ${item.veg_type === 'VEG' ? 'border-green-600 text-green-600' : 'border-red-600 text-red-600'}`}>
                                                ●
                                            </span>
                                            <h3 className="font-bold text-lg text-gray-900 line-clamp-1">{item.name}</h3>
                                            <button
                                                onClick={() => toggleFavItem(item.id)}
                                                className={`ml-2 p-1 rounded-full transition-colors ${item.is_favourite ? 'text-red-500' : 'text-gray-300 hover:text-red-400'}`}
                                            >
                                                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill={item.is_favourite ? "currentColor" : "none"} stroke="currentColor">
                                                    <path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" />
                                                </svg>
                                            </button>
                                        </div>
                                        <p className="text-gray-500 text-xs mb-3 line-clamp-2 font-medium leading-normal">{item.description}</p>
                                        <p className="font-black text-xl text-gray-900">₹{item.price}</p>
                                    </div>

                                    <div className="relative flex-shrink-0">
                                        <div className="h-24 w-24 rounded-xl overflow-hidden shadow-sm border border-gray-100 bg-gray-50">
                                            {(() => { const dishImg = getMediaImageUrl(item.image_url) || item.image_url; return dishImg ? (
                                                <img
                                                    src={dishImg}
                                                    alt={item.name}
                                                    className="w-full h-full object-cover"
                                                    onError={(e) => { e.target.style.display = 'none'; }}
                                                />
                                            ) : (
                                                <div className="w-full h-full flex items-center justify-center text-3xl">
                                                    🍜
                                                </div>
                                            ); })()}
                                        </div>

                                        <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-20">
                                            {quantity > 0 ? (
                                                <div className="flex items-center justify-between bg-white border border-red-100 rounded-lg overflow-hidden shadow-lg h-8">
                                                    <button
                                                        className="flex-1 text-red-600 font-black hover:bg-red-50 transition-colors"
                                                        onClick={() => updateQuantity(item.id, -1)}
                                                    >-</button>
                                                    <span className="px-1 text-xs font-black text-gray-900">{quantity}</span>
                                                    <button
                                                        className="flex-1 text-red-600 font-black hover:bg-red-50 transition-colors"
                                                        onClick={() => updateQuantity(item.id, 1)}
                                                    >+</button>
                                                </div>
                                            ) : (
                                                <button
                                                    className="w-full bg-white text-red-600 border border-red-100 h-8 rounded-lg font-black text-xs hover:bg-red-50 transition shadow-md active:scale-95"
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

            {/* Floating Cart Button - Refined */}
            {cartItems.length > 0 && (
                <div className="fixed bottom-6 left-1/2 -translate-x-1/2 w-[calc(100%-2rem)] max-w-lg z-50">
                    <Link to="/client/cart">
                        <motion.div
                            initial={{ y: 50, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            className="bg-gray-900 text-white px-6 py-4 rounded-2xl shadow-2xl flex justify-between items-center hover:bg-black transition cursor-pointer group"
                        >
                            <div className="flex items-center gap-4">
                                <div className="bg-red-600 px-2.5 py-1 rounded-lg">
                                    <span className="font-black text-base">{getCartCount()}</span>
                                </div>
                                <div className="flex flex-col">
                                    <span className="font-black text-sm tracking-tight uppercase">View Cart</span>
                                    <span className="text-[10px] opacity-70 font-bold tracking-widest uppercase">Total: ₹{getCartTotal().toFixed(2)}</span>
                                </div>
                            </div>
                            <div className="flex items-center font-black text-sm gap-2 uppercase group-hover:gap-4 transition-all">
                                Checkout <span className="text-xl">→</span>
                            </div>
                        </motion.div>
                    </Link>
                </div>
            )}
        </div>
    );
};
export default RestaurantDetails;
