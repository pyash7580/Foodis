import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import Navbar from '../../components/Navbar';
import RestaurantCard from '../../components/RestaurantCard';
import DishCard from '../../components/DishCard';
import LocationDetector from '../../components/LocationDetector';
import { motion } from 'framer-motion';
import { API_BASE_URL } from '../../config';

import { useAuth } from '../../contexts/AuthContext';

const Home = () => {
    const { token } = useAuth();
    const [restaurants, setRestaurants] = useState([]);
    const [filteredRestaurants, setFilteredRestaurants] = useState([]);

    // Search & Filter State
    const [searchMode, setSearchMode] = useState('restaurant'); // 'restaurant' or 'dish'
    const [dishResults, setDishResults] = useState([]);
    const [isSearching, setIsSearching] = useState(false);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [activeFilter, setActiveFilter] = useState('All');
    const [sortBy, setSortBy] = useState('rating'); // rating, cost_low, cost_high
    const [selectedCity, setSelectedCity] = useState(''); // Track selected city for filtering

    // Animation Variants
    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1
            }
        }
    };

    const categories = [
        { name: 'Pizza', icon: '🍕' },
        { name: 'Biryani', icon: '🥘' },
        { name: 'Burger', icon: '🍔' },
        { name: 'Chinese', icon: '🍜' },
        { name: 'Healthy', icon: '🥗' },
        { name: 'Dessert', icon: '🍰' },
    ];

    const fetchRestaurants = useCallback(async () => {
        // Build URL with city filter if selected
        let url = `${API_BASE_URL}/api/client/restaurants/`;
        if (selectedCity) {
            url += `?city=${encodeURIComponent(selectedCity)}`;
        }

        try {
            setLoading(true);
            const config = token ? { headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' } } : {};
            const response = await axios.get(url, config);
            const data = response.data.results || response.data;
            setRestaurants(data);
            setFilteredRestaurants(data);
            setError(null);
            setLoading(false);
        } catch (err) {
            console.error("Failed to fetch restaurants:", err);
            if (!err.response || err.response.status !== 401) {
                setError("Failed to load restaurants. Please try again later.");
            }
            setLoading(false);
        }
    }, [selectedCity, token]);

    useEffect(() => {
        fetchRestaurants();
    }, [fetchRestaurants]);

    const searchDishes = useCallback(async () => {
        if (searchMode === 'dish') {
            setIsSearching(true);
            try {
                const url = searchQuery.length > 0
                    ? `${API_BASE_URL}/api/client/menu-items/?search=${searchQuery}`
                    : `${API_BASE_URL}/api/client/menu-items/`;

                const config = token ? { headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' } } : {};
                const response = await axios.get(url, config);
                const data = response.data.results || response.data;
                const uniqueDishes = Array.from(new Map(data.map(item => [item.id, item])).values());
                setDishResults(uniqueDishes);
            } catch (err) {
                console.error("Dish search error", err);
            } finally {
                setIsSearching(false);
            }
        }
    }, [searchQuery, searchMode, token]);

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            if (searchMode === 'dish') searchDishes();
        }, 500);
        return () => clearTimeout(timeoutId);
    }, [searchQuery, searchMode, searchDishes]);

    useEffect(() => {
        if (searchMode !== 'restaurant') return;

        let result = [...restaurants];
        if (searchQuery) {
            result = result.filter(r =>
                r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                (r.cuisine && r.cuisine.toLowerCase().includes(searchQuery.toLowerCase()))
            );
        }
        if (activeFilter !== 'All') {
            result = result.filter(r => r.cuisine && r.cuisine.toLowerCase().includes(activeFilter.toLowerCase()));
        }
        if (sortBy === 'rating') {
            result.sort((a, b) => b.rating - a.rating);
        } else if (sortBy === 'cost_low') {
            result.sort((a, b) => a.delivery_fee - b.delivery_fee);
        } else if (sortBy === 'cost_high') {
            result.sort((a, b) => b.delivery_fee - a.delivery_fee);
        }
        setFilteredRestaurants(result);
    }, [restaurants, searchQuery, activeFilter, sortBy, searchMode]);

    return (
        <div className="min-h-screen bg-white">
            <Navbar />
            <div className="bg-white sticky top-0 z-40 border-b border-gray-100 shadow-sm">
                <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <LocationDetector onLocationDetected={(location) => {
                            if (location && location.city) {
                                setSelectedCity(location.city);
                            }
                        }} />
                        <div className="flex-1 max-w-3xl w-full">
                            <div className="flex items-center gap-2 mb-2">
                                <button
                                    onClick={() => { setSearchMode('restaurant'); setSearchQuery(''); }}
                                    className={`px-4 py-1.5 rounded-full text-sm font-black transition-all ${searchMode === 'restaurant' ? 'bg-gray-900 text-white shadow-lg' : 'text-gray-400 hover:text-gray-600'}`}
                                >
                                    Restaurants
                                </button>
                                <button
                                    onClick={() => { setSearchMode('dish'); setSearchQuery(''); }}
                                    className={`px-4 py-1.5 rounded-full text-sm font-black transition-all ${searchMode === 'dish' ? 'bg-red-600 text-white shadow-lg' : 'text-gray-400 hover:text-red-500'}`}
                                >
                                    Dishes
                                </button>
                            </div>
                            <div className="relative group">
                                <input
                                    type="text"
                                    placeholder={searchMode === 'restaurant' ? "Search for restaurants, cuisines..." : "Search for dishes (e.g. Paneer, Pizza)..."}
                                    className="w-full pl-12 pr-4 py-3 rounded-2xl border border-gray-200 focus:outline-none focus:ring-4 focus:ring-red-50 focus:border-red-500 bg-gray-50 group-hover:bg-white transition-all shadow-sm font-bold text-gray-700"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                />
                                <span className="absolute left-4 top-3.5 text-gray-400 text-xl">
                                    {isSearching ? <div className="animate-spin h-5 w-5 border-2 border-red-500 border-t-transparent rounded-full"></div> : '🔍'}
                                </span>
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center gap-4 mt-4 overflow-x-auto pb-2 no-scrollbar">
                        {categories.map(cat => (
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                key={cat.name}
                                onClick={() => {
                                    if (searchMode === 'restaurant') {
                                        setActiveFilter(activeFilter === cat.name ? 'All' : cat.name);
                                    } else {
                                        setSearchQuery(cat.name);
                                    }
                                }}
                                className={`flex items-center gap-2 px-5 py-2.5 rounded-2xl whitespace-nowrap transition-all border font-bold ${(searchMode === 'restaurant' && activeFilter === cat.name) || (searchMode === 'dish' && searchQuery === cat.name)
                                    ? 'bg-red-600 border-red-600 text-white shadow-lg'
                                    : 'bg-white border-gray-200 text-gray-600 hover:border-red-200 hover:bg-red-50'
                                    }`}
                            >
                                <span>{cat.icon}</span>
                                <span>{cat.name}</span>
                            </motion.button>
                        ))}
                    </div>
                </div>
            </div>
            <main className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-10">
                <div className="flex items-center justify-between mb-8">
                    <h2 className="text-3xl font-black text-gray-900">
                        {searchMode === 'restaurant'
                            ? (activeFilter === 'All' ? 'Best Restaurants for You' : `${activeFilter} Restaurants`)
                            : (searchQuery ? `Dish Results for "${searchQuery}"` : 'Search for your favorite dishes')
                        }
                    </h2>
                    {searchMode === 'restaurant' && (
                        <div className="flex items-center gap-2 bg-gray-100 p-1 rounded-xl">
                            <button
                                onClick={() => setSortBy('rating')}
                                className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${sortBy === 'rating' ? 'bg-white text-red-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                            >
                                Rating
                            </button>
                            <button
                                onClick={() => setSortBy('cost_low')}
                                className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${sortBy === 'cost_low' ? 'bg-white text-red-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                            >
                                Price: Low to High
                            </button>
                        </div>
                    )}
                </div>
                {loading && searchMode === 'restaurant' ? (
                    <div className="flex flex-col items-center justify-center h-64 gap-4">
                        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-red-600"></div>
                        <p className="text-gray-500 font-bold">Curating the best options for you...</p>
                    </div>
                ) : error ? (
                    <div className="text-center py-20 bg-red-50 rounded-3xl border border-red-100 p-8">
                        <div className="text-6xl mb-4">🏠</div>
                        <h3 className="text-2xl font-bold text-red-800 mb-2">{error}</h3>
                        <p className="text-red-600 mb-6">Seems like our kitchen is currently busy. Please check back in a moment.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="bg-red-600 text-white px-8 py-3 rounded-2xl font-bold shadow-lg hover:bg-red-700 transition-all"
                        >
                            Retry Loading
                        </button>
                    </div>
                ) : (
                    <>
                        {searchMode === 'restaurant' && (
                            filteredRestaurants.length === 0 ? (
                                <div className="text-center py-20">
                                    <div className="text-7xl mb-6">🔍</div>
                                    <h3 className="text-2xl font-bold text-gray-900 mb-2">No restaurants found</h3>
                                    <p className="text-gray-500">Try adjusting your filters or search query</p>
                                </div>
                            ) : (
                                <motion.div
                                    variants={containerVariants}
                                    initial="hidden"
                                    animate="visible"
                                    className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-10"
                                >
                                    {filteredRestaurants.map((restaurant, index) => (
                                        <RestaurantCard key={restaurant.id} restaurant={restaurant} index={index} />
                                    ))}
                                </motion.div>
                            )
                        )}
                        {searchMode === 'dish' && (
                            dishResults.length === 0 && !isSearching ? (
                                <div className="text-center py-20">
                                    <div className="text-7xl mb-6">🍛</div>
                                    <h3 className="text-2xl font-bold text-gray-900 mb-2">{searchQuery ? 'No dishes found' : 'Loading delicious dishes...'}</h3>
                                    <p className="text-gray-500">{searchQuery ? 'Try a different keyword like "Pizza", "Cake", or "Paneer"' : 'We are curating the best dishes for you!'}</p>
                                </div>
                            ) : (
                                <motion.div
                                    variants={containerVariants}
                                    initial="hidden"
                                    animate="visible"
                                    className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
                                >
                                    {dishResults.map((dish) => (
                                        <DishCard key={dish.id} item={dish} />
                                    ))}
                                </motion.div>
                            )
                        )}
                    </>
                )}
            </main>
        </div>
    );
};

export default Home;
