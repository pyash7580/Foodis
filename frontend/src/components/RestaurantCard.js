import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

const RestaurantCard = ({ restaurant, index }) => {
    const { token } = useAuth();
    const [isFav, setIsFav] = useState(restaurant.is_favourite);
    const [imageLoaded, setImageLoaded] = useState(true);

    // Generate a consistent random color for placeholder if no image
    const colors = ['bg-red-100', 'bg-blue-100', 'bg-green-100', 'bg-yellow-100', 'bg-purple-100'];
    const colorClass = colors[restaurant.id % colors.length] || 'bg-gray-100';

    const toggleFavorite = async (e) => {
        e.preventDefault();
        e.stopPropagation();

        if (!token) {
            toast.error("Please login to favourite restaurants");
            return;
        }

        try {
            const res = await axios.post(`${API_BASE_URL}/api/client/favourite-restaurants/toggle/`,
                { restaurant_id: restaurant.id },
                { headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' } }
            );

            const newStatus = res.data.status === 'added';
            setIsFav(newStatus);
            toast.success(newStatus ? "Added to favourites!" : "Removed from favourites");
        } catch (err) {
            toast.error("Failed to update favourites");
        }
    };

    const handleImageError = () => {
        setImageLoaded(false);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: index * 0.1 }}
            className="relative"
        >
            <Link to={`/client/restaurants/${restaurant.id}`} className="block group">
                <div className={`rounded-2xl overflow-hidden shadow-sm hover:shadow-2xl transition-all duration-500 bg-white border border-gray-100 ${colorClass} h-full`}>
                    <div className="h-52 w-full bg-cover bg-center relative group-hover:scale-105 transition-transform duration-700 flex items-center justify-center"
                        style={imageLoaded && (restaurant.image_url || restaurant.cover_image_url || restaurant.image) ? { backgroundImage: `url(${restaurant.image_url || restaurant.cover_image_url || restaurant.image}?t=${new Date(restaurant.updated_at || Date.now()).getTime()})` } : {}}>
                        {/* Image element for error detection */}
                        {imageLoaded && (restaurant.image_url || restaurant.cover_image_url || restaurant.image) && (
                            <img
                                src={`${restaurant.image_url || restaurant.cover_image_url || restaurant.image}?t=${new Date(restaurant.updated_at || Date.now()).getTime()}`}
                                alt={restaurant.name}
                                onError={handleImageError}
                                className="hidden"
                                crossOrigin="anonymous"
                            />
                        )}
                        {/* Fallback when no image or image fails to load */}
                        {!imageLoaded || (!restaurant.image_url && !restaurant.cover_image_url && !restaurant.image) ? (
                            <div className={`w-full h-full flex items-center justify-center ${colorClass}`}>
                                <span className="text-5xl">🍽️</span>
                            </div>
                        ) : null}

                        {/* Favorite Button */}
                        <button
                            onClick={toggleFavorite}
                            className={`absolute top-3 left-3 p-2 rounded-full backdrop-blur-md transition-all duration-300 z-10 ${isFav ? 'bg-red-500 text-white shadow-lg' : 'bg-white/70 text-gray-700 hover:bg-white'
                                }`}
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill={isFav ? "currentColor" : "none"} stroke="currentColor" strokeWidth={isFav ? "0" : "1.5"}>
                                <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                            </svg>
                        </button>

                        <div className="absolute top-3 right-3 bg-white/90 backdrop-blur-sm px-2 py-1 rounded-lg text-xs font-bold shadow-md">
                            {restaurant.delivery_time} mins
                        </div>
                        {restaurant.rating >= 4.5 && (
                            <div className="absolute bottom-3 left-3 bg-red-600 text-white px-2 py-1 rounded-lg text-xs font-bold shadow-md z-0">
                                Best Safety
                            </div>
                        )}
                    </div>
                    <div className="p-4 bg-white">
                        <div className="flex justify-between items-start">
                            <h3 className="text-xl font-extrabold text-gray-900 group-hover:text-red-600 transition-colors line-clamp-1">
                                {restaurant.name}
                            </h3>
                            <span className="flex items-center bg-green-600 px-2 py-0.5 rounded text-white text-xs font-bold shadow-sm">
                                {restaurant.rating} ★
                            </span>
                        </div>
                        <p className="text-sm text-gray-500 mt-1 line-clamp-1 font-medium">{restaurant.cuisine}</p>
                        <div className="mt-4 pt-3 border-t border-gray-50 flex items-center justify-between text-xs text-gray-500 font-semibold italic">
                            <span>{restaurant.city}</span>
                            <span className="text-gray-900">₹{restaurant.delivery_fee} delivery</span>
                        </div>
                    </div>
                </div>
            </Link>
        </motion.div>
    );
};

export default React.memo(RestaurantCard);
