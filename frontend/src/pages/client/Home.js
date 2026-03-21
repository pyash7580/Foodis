import React, { useEffect, useState, useCallback, useRef } from 'react';
import axios from 'axios';
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

    // FIX: start as false — show page immediately; only show spinner while fetching after city detected
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [activeFilter, setActiveFilter] = useState('All');
    const [sortBy, setSortBy] = useState('rating'); // rating, cost_low, cost_high
    const [selectedCity, setSelectedCity] = useState(''); // Track selected city for filtering
    // eslint-disable-next-line no-unused-vars
    const [_userLocation, setUserLocation] = useState(null); // Track coordinates for live location

    // FIX: abort controller ref to cancel stale dish search requests
    const searchAbortRef = useRef(null);

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

    const handleLocationDetected = useCallback((location) => {
        if (location) {
            if ('city' in location) {
                setSelectedCity(location.city || '');
                setUserLocation(null);
            } else if (location.latitude && location.longitude) {
                setUserLocation({ latitude: location.latitude, longitude: location.longitude });
                setSelectedCity('');
            }
        }
    }, []);

    const fetchRestaurants = useCallback(async (city) => {
        setLoading(true);
        try {
            let url = `${API_BASE_URL}/api/client/restaurants/`;
            if (city) url += `?city=${encodeURIComponent(city)}`;

            const config = token ? { headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' } } : {};
            const res = await axios.get(url, config);

            let data = res.data;
            // Handle all possible response shapes
            if (data && data.results) data = data.results;
            else if (data && data.data) data = data.data;
            else if (!Array.isArray(data)) data = [];

            setRestaurants(data);
            setFilteredRestaurants(data);
            setError(null);
        } catch (err) {
            setRestaurants([]);
            setFilteredRestaurants([]);
            setError("Failed to load restaurants.");
        } finally {
            setLoading(false);
        }
    }, [token]);

    // FIX: Only fetch when selectedCity changes — prevents double-call on mount.
    // LocationDetector sets selectedCity, which triggers this fetch exactly once.
    useEffect(() => {
        fetchRestaurants(selectedCity);
    }, [selectedCity, fetchRestaurants]);

    const searchDishes = useCallback(async () => {
        if (searchMode === 'dish') {
            // Cancel any previous in-flight request
            if (searchAbortRef.current) searchAbortRef.current.abort();
            searchAbortRef.current = new AbortController();

            setIsSearching(true);
            try {
                const url = searchQuery.length > 0
                    ? `${API_BASE_URL}/api/client/menu-items/?search=${encodeURIComponent(searchQuery)}`
                    : `${API_BASE_URL}/api/client/menu-items/`;

                const config = {
                    signal: searchAbortRef.current.signal,
                    ...(token ? { headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' } } : {})
                };
                const response = await axios.get(url, config);
                const data = response.data.results || response.data;
                const uniqueDishes = Array.from(new Map(data.map(item => [item.id, item])).values());
                setDishResults(uniqueDishes);
            } catch (err) {
                // Ignore abort errors (user typed faster than request completed)
                if (err.name === 'CanceledError' || err.name === 'AbortError') return;
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
            result = result.filter(r => {
                const cuisineMatch = r.cuisine && r.cuisine.toLowerCase().includes(activeFilter.toLowerCase());
                const cuisineTypeMatch = r.cuisine_type && r.cuisine_type.toLowerCase().includes(activeFilter.toLowerCase());
                const cuisineTypesMatch = Array.isArray(r.cuisine_types) &&
                    r.cuisine_types.some(ct => ct.toLowerCase().includes(activeFilter.toLowerCase()));
                const nameMatch = r.name && r.name.toLowerCase().includes(activeFilter.toLowerCase());
                return cuisineMatch || cuisineTypeMatch || cuisineTypesMatch || nameMatch;
            });
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
        <div className="min-h-screen bg-gray-50 flex flex-col relative w-full overflow-x-hidden">
            {/* Mobile Top App Bar */}
            <div className="md:hidden bg-white px-4 pt-12 pb-4 shadow-sm sticky top-0 z-40 relative">
                <div className="flex justify-between items-center mb-3">
                    <div>
                        <p className="text-xs text-gray-500 font-bold uppercase tracking-wider mb-0.5">Delivering to</p>
                        <LocationDetector onLocationDetected={handleLocationDetected} compact={true} />
                    </div>
                    <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center overflow-hidden">
                        <span className="text-xl">👤</span>
                    </div>
                </div>
            </div>

            {/* Desktop Header Container (Hidden on Mobile) */}
            <div className="hidden md:block bg-white sticky top-0 z-40 border-b border-gray-100 shadow-sm">
                <div className="w-full mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <LocationDetector onLocationDetected={handleLocationDetected} />
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
                                <span className="text-[13px] md:text-base">{cat.name}</span>
                            </motion.button>
                        ))}
                    </div>
                </div>
            </div>
            <main className="w-full mx-auto px-4 sm:px-6 lg:px-8 py-10">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-8 gap-4">
                    <h2 className="text-3xl font-black text-gray-900 leading-tight">
                        {searchMode === 'restaurant'
                            ? (activeFilter === 'All' ? 'Best Restaurants for You' : `${activeFilter} Restaurants`)
                            : (searchQuery ? `Dish Results for "${searchQuery}"` : 'Search for your favorite dishes')
                        }
                    </h2>
                    {searchMode === 'restaurant' && (
                        <div className="flex items-center gap-2 bg-gray-100 p-1.5 rounded-xl w-full sm:w-auto overflow-x-auto no-scrollbar">
                            <button
                                onClick={() => setSortBy('rating')}
                                className={`flex-1 sm:flex-none px-4 py-2 rounded-lg text-sm font-bold transition-all whitespace-nowrap ${sortBy === 'rating' ? 'bg-white text-red-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                            >
                                Rating
                            </button>
                            <button
                                onClick={() => setSortBy('cost_low')}
                                className={`flex-1 sm:flex-none px-4 py-2 rounded-lg text-sm font-bold transition-all whitespace-nowrap ${sortBy === 'cost_low' ? 'bg-white text-red-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
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
