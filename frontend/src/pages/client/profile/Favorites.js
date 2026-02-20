import { API_BASE_URL } from '../../../config';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';

import { useAuth } from '../../../contexts/AuthContext';

const Favorites = () => {
    const { token } = useAuth();
    const [activeTab, setActiveTab] = useState('restaurants');
    const [favRestaurants, setFavRestaurants] = useState([]);
    const [favDishes, setFavDishes] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (token) {
            fetchFavorites();
        }
    }, [token]);

    const fetchFavorites = async () => {
        try {
            const [restRes, dishRes] = await Promise.all([
                axios.get(`${API_BASE_URL}/api/client/favourite-restaurants/`, {
                    headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
                }),
                axios.get(`${API_BASE_URL}/api/client/favourite-menu-items/`, {
                    headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
                })
            ]);
            // Handle paginated response for Restaurants
            if (restRes.data.results && Array.isArray(restRes.data.results)) {
                setFavRestaurants(restRes.data.results);
            } else if (Array.isArray(restRes.data)) {
                setFavRestaurants(restRes.data);
            } else {
                setFavRestaurants([]);
            }

            // Handle paginated response for Dishes
            if (dishRes.data.results && Array.isArray(dishRes.data.results)) {
                setFavDishes(dishRes.data.results);
            } else if (Array.isArray(dishRes.data)) {
                setFavDishes(dishRes.data);
            } else {
                setFavDishes([]);
            }

            setLoading(false);
        } catch (error) {
            console.error(error);
            setLoading(false);
        }
    };

    const removeRestaurant = async (id) => {
        try {
            await axios.delete(`${API_BASE_URL}/api/client/favourite-restaurants/${id}/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
            });
            toast.success("Removed from favorites");
            fetchFavorites();
        } catch (error) {
            toast.error("Failed to remove");
        }
    };

    // Note: Dish remove logic similar if API supports ID deletion or via item ID logic

    if (loading) return <div className="p-8 text-center text-gray-400 font-bold">Loading Favorites...</div>;

    return (
        <div className="space-y-8">
            <header>
                <h1 className="text-2xl font-black text-gray-900">My Favorites</h1>
            </header>

            <div className="flex space-x-2 border-b border-gray-100">
                <button
                    onClick={() => setActiveTab('restaurants')}
                    className={`px-6 py-3 font-bold text-sm transition ${activeTab === 'restaurants' ? 'text-red-600 border-b-2 border-red-600' : 'text-gray-500 hover:text-gray-900'}`}
                >
                    Restaurants
                </button>
                <button
                    onClick={() => setActiveTab('dishes')}
                    className={`px-6 py-3 font-bold text-sm transition ${activeTab === 'dishes' ? 'text-red-600 border-b-2 border-red-600' : 'text-gray-500 hover:text-gray-900'}`}
                >
                    Dishes
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {activeTab === 'restaurants' && Array.isArray(favRestaurants) && favRestaurants.map(item => (
                    <div key={item.id} className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 flex gap-4 relative group">
                        <div className="w-24 h-24 bg-gray-100 rounded-xl overflow-hidden flex-shrink-0">
                            {item.restaurant_details.image ? (
                                <img src={item.restaurant_details.image} alt={item.restaurant_details.name} className="w-full h-full object-cover" />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center text-2xl">🏪</div>
                            )}
                        </div>
                        <div className="flex-1">
                            <h3 className="font-black text-gray-900 text-lg leading-tight">{item.restaurant_details.name}</h3>
                            <p className="text-xs text-gray-500 mt-1">{item.restaurant_details.cuisine || 'Multi-cuisine'}</p>
                            <p className="text-xs text-gray-400 mt-1">{item.restaurant_details.city}</p>
                            <div className="mt-3 flex space-x-2">
                                <Link to={`/client/restaurants/${item.restaurant_details.id}`} className="px-3 py-1 bg-red-50 text-red-600 text-xs font-bold rounded-lg hover:bg-red-100 transition">
                                    Order Now
                                </Link>
                                <button onClick={() => removeRestaurant(item.id)} className="px-3 py-1 bg-gray-100 text-gray-500 text-xs font-bold rounded-lg hover:bg-gray-200 transition">
                                    Remove
                                </button>
                            </div>
                        </div>
                    </div>
                ))}

                {activeTab === 'dishes' && Array.isArray(favDishes) && favDishes.map(item => (
                    <div key={item.id} className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 flex gap-4 relative group">
                        <div className="w-24 h-24 bg-gray-100 rounded-xl overflow-hidden flex-shrink-0">
                            {item.menu_item_details.image ? (
                                <img src={item.menu_item_details.image} alt={item.menu_item_details.name} className="w-full h-full object-cover" />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center text-2xl">🥘</div>
                            )}
                        </div>
                        <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                                <span className={`w-3 h-3 rounded-full ${item.menu_item_details.veg_type === 'VEG' ? 'bg-green-500' : 'bg-red-500'}`}></span>
                                <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">{item.menu_item_details.veg_type}</span>
                            </div>
                            <h3 className="font-black text-gray-900 text-lg leading-tight">{item.menu_item_details.name}</h3>
                            <p className="text-red-600 font-bold mt-1">₹{item.menu_item_details.price}</p>

                            <div className="mt-3 flex space-x-2">
                                <Link to={`/client/restaurants/${item.menu_item_details.restaurant}`} className="px-3 py-1 bg-red-50 text-red-600 text-xs font-bold rounded-lg hover:bg-red-100 transition">
                                    View Restaurant
                                </Link>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {((activeTab === 'restaurants' && favRestaurants.length === 0) || (activeTab === 'dishes' && favDishes.length === 0)) && (
                <div className="text-center py-12 bg-white rounded-3xl border border-dashed border-gray-200">
                    <p className="text-gray-400 font-bold">No favorites found.</p>
                    <Link to="/client" className="inline-block mt-4 text-red-600 font-bold hover:underline">Explore Restaurants</Link>
                </div>
            )}
        </div>
    );
};

export default Favorites;
