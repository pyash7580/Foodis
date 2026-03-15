import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { FaSearch, FaArrowLeft, FaStar, FaStore } from 'react-icons/fa';
import { API_BASE_URL } from '../../config';
import { useAuth } from '../../contexts/AuthContext';
import { useCart } from '../../contexts/CartContext';
import toast from 'react-hot-toast';

const Search = () => {
    const navigate = useNavigate();
    const { token } = useAuth();
    const { addToCart, getCartCount } = useCart();
    
    const [query, setQuery] = useState('');
    const [activeTab, setActiveTab] = useState('restaurants'); // 'restaurants' | 'dishes'
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState({ restaurants: [], menu_items: [], recommendations: [] });
    const [location, setLocation] = useState(null);

    // Get user location on mount if possible to sort results by distance
    useEffect(() => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    setLocation({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    });
                },
                () => {
                    console.log("Geolocation permission denied or unavailable.");
                }
            );
        }
    }, []);

    const performSearch = useCallback(async (searchQuery) => {
        if (!searchQuery.trim()) {
            setResults({ restaurants: [], menu_items: [], recommendations: [] });
            return;
        }

        setLoading(true);
        try {
            let url = `${API_BASE_URL}/api/client/search/?q=${encodeURIComponent(searchQuery)}`;
            if (location) {
                url += `&latitude=${location.latitude}&longitude=${location.longitude}&radius=80`;
            }

            const response = await axios.get(url, {
                headers: token ? { Authorization: `Bearer ${token}` } : {}
            });
            setResults(response.data);
        } catch (error) {
            console.error('Search failed:', error);
            toast.error("Failed to search. Please try again.");
        } finally {
            setLoading(false);
        }
    }, [location, token]);

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            performSearch(query);
        }, 500);
        return () => clearTimeout(timer);
    }, [query, performSearch]);

    const handleAddToCart = (item, e) => {
        e.stopPropagation();
        
        // Ensure item has a restaurant object attached for checking
        // In the search API, the menu_items typically return the restaurant ID or object.
        // If the backend doesn't return full nested objects, we'll need a fallback.
        const restaurantContext = typeof item.restaurant === 'object' 
            ? item.restaurant 
            : { id: item.restaurant };
            
        addToCart(item, restaurantContext);
        toast.success(`Added ${item.name} to cart!`, { duration: 1500 });
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col relative pb-20 md:pb-0">
            {/* Top App Bar with Embedded Search Input */}
            <div className="bg-white sticky top-0 z-50 pt-safe-top shadow-sm px-4 pb-3 border-b border-gray-100">
                <div className="flex items-center h-14">
                    <button
                        onClick={() => navigate(-1)}
                        className="p-2 -ml-2 text-gray-800 focus:outline-none"
                    >
                        <FaArrowLeft className="text-xl" />
                    </button>
                    
                    <div className="flex-1 ml-2 relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <FaSearch className="text-gray-400" />
                        </div>
                        <input
                            type="text"
                            autoFocus
                            placeholder="Restaurants or dishes..."
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            className="block w-full pl-10 pr-3 py-2 border border-gray-200 rounded-xl leading-5 bg-gray-50 focus:outline-none focus:ring-1 focus:ring-red-500 focus:border-red-500 text-base sm:text-sm text-gray-900 placeholder-gray-500 transition-colors"
                        />
                        {query && (
                            <button 
                                onClick={() => setQuery('')}
                                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                            >
                                ✕
                            </button>
                        )}
                    </div>
                </div>

                {/* Animated Tabs */}
                <div className="flex mt-3 bg-gray-100 p-1 rounded-xl relative">
                    {['restaurants', 'dishes'].map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`flex-1 py-1.5 text-sm font-bold relative z-10 capitalize transition-colors duration-200 ${
                                activeTab === tab ? 'text-gray-900' : 'text-gray-500 hover:text-gray-700'
                            }`}
                        >
                            {tab}
                            {activeTab === tab && (
                                <motion.div
                                    layoutId="searchTabBackground"
                                    className="absolute inset-0 bg-white rounded-lg shadow-sm -z-10"
                                    transition={{ type: "spring", stiffness: 400, damping: 30 }}
                                />
                            )}
                        </button>
                    ))}
                </div>
            </div>

            {/* Scrollable Content Area */}
            <div className="flex-1 overflow-y-auto px-4 py-6">
                {!query ? (
                    <div className="h-full flex flex-col items-center justify-center text-center mt-20">
                        <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4 text-gray-300">
                            <FaSearch className="text-4xl" />
                        </div>
                        <h2 className="text-xl font-black text-gray-800 mb-2">What are you craving?</h2>
                        <p className="text-gray-500 text-sm max-w-[250px]">
                            Search for your favorite restaurants, dishes, or cuisines.
                        </p>
                    </div>
                ) : loading ? (
                    <div className="flex justify-center mt-12">
                        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-red-600"></div>
                    </div>
                ) : (
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={activeTab}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            transition={{ duration: 0.2 }}
                        >
                            {/* RESTAURANTS TAB */}
                            {activeTab === 'restaurants' && (
                                <div className="space-y-4">
                                    {results.restaurants.length > 0 ? (
                                        results.restaurants.map((restaurant) => (
                                            <div 
                                                key={restaurant.id} 
                                                onClick={() => navigate(`/client/restaurants/${restaurant.id}`)}
                                                className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden active:scale-[0.98] transition-transform cursor-pointer"
                                            >
                                                <div className="flex h-24">
                                                    <div className="h-full w-24 bg-gray-200 shrink-0 relative overflow-hidden">
                                                        {restaurant.image ? (
                                                            <img src={restaurant.image} alt={restaurant.name} className="w-full h-full object-cover" />
                                                        ) : (
                                                            <div className="w-full h-full flex items-center justify-center text-gray-400">
                                                                <FaStore size={24} />
                                                            </div>
                                                        )}
                                                        {restaurant.status === 'APPROVED' && restaurant.is_active && (
                                                            <div className="absolute top-0 right-0 bg-white/90 px-1 py-0.5 rounded-bl-lg">
                                                                <div className="flex items-center text-xs font-bold text-green-700">
                                                                    <FaStar className="text-[10px] mr-1" /> {restaurant.rating || 'New'}
                                                                </div>
                                                            </div>
                                                        )}
                                                    </div>
                                                    <div className="flex-1 p-3 flex flex-col justify-center">
                                                        <h3 className="font-black text-gray-900 leading-tight">{restaurant.name}</h3>
                                                        <p className="text-xs text-gray-500 mt-1 line-clamp-1">{restaurant.description || 'Fast Food  •  Beverages'}</p>
                                                        <div className="mt-2 flex gap-3 text-xs font-bold text-gray-400">
                                                            <span>• 30-40 mins</span>
                                                            <span>• ₹200 for one</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        ))
                                    ) : (
                                        <div className="text-center py-10">
                                            <p className="text-gray-500 font-medium">No restaurants found matching "{query}"</p>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* DISHES TAB */}
                            {activeTab === 'dishes' && (
                                <div className="space-y-4">
                                    {results.menu_items.length > 0 ? (
                                        results.menu_items.map((item) => (
                                            <div key={item.id} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
                                                <div className="flex justify-between gap-4">
                                                    <div className="flex-1">
                                                        <div className="flex items-center gap-2 mb-1">
                                                            <div className={`w-3 h-3 rounded-sm border ${item.dietary_preference === 'VEG' ? 'border-green-600' : 'border-red-600'} flex items-center justify-center`}>
                                                                <div className={`w-1.5 h-1.5 rounded-full ${item.dietary_preference === 'VEG' ? 'bg-green-600' : 'bg-red-600'}`}></div>
                                                            </div>
                                                            {item.is_bestseller && (
                                                                <span className="text-[10px] font-black tracking-widest uppercase text-yellow-600 bg-yellow-100 px-1.5 py-0.5 rounded">Bestseller</span>
                                                            )}
                                                        </div>
                                                        
                                                        <h3 className="font-black text-gray-900 text-lg leading-tight">{item.name}</h3>
                                                        <div className="font-bold text-gray-800 mt-1">₹{item.price}</div>
                                                        
                                                        {item.description && (
                                                            <p className="text-xs text-gray-500 mt-2 line-clamp-2 leading-relaxed">
                                                                {item.description}
                                                            </p>
                                                        )}
                                                    </div>
                                                    
                                                    <div className="w-28 flex flex-col items-center">
                                                        <div className="w-28 h-28 rounded-xl bg-gray-100 overflow-hidden mb-[-20px] shadow-sm relative">
                                                            {item.image ? (
                                                                <img src={item.image} alt={item.name} className="w-full h-full object-cover" />
                                                            ) : (
                                                                <div className="w-full h-full flex items-center justify-center text-gray-300">
                                                                    🍲
                                                                </div>
                                                            )}
                                                        </div>
                                                        <button
                                                            onClick={(e) => handleAddToCart(item, e)}
                                                            className="bg-white border text-red-600 border-red-100 shadow-md font-black text-sm px-6 py-2 rounded-lg active:scale-95 transition-transform"
                                                        >
                                                            ADD
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        ))
                                    ) : (
                                        <div className="text-center py-10">
                                            <p className="text-gray-500 font-medium">No dishes found matching "{query}"</p>
                                        </div>
                                    )}
                                </div>
                            )}
                        </motion.div>
                    </AnimatePresence>
                )}
            </div>
            
        </div>
    );
};

export default Search;
