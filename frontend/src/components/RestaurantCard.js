import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import ImageWithFallback from './ImageWithFallback';

// Helper to get correct image URL
const getImageSrc = (imageUrl) => {
    if (!imageUrl) return null;
    if (imageUrl.startsWith('http')) return imageUrl;
    // Local media file — prepend backend URL
    const backendUrl = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';
    return `${backendUrl}${imageUrl.startsWith('/') ? '' : '/'}${imageUrl}`;
};

// Image component with fallback
const RestaurantImage = ({ src, name }) => {
    const [error, setError] = React.useState(false);
    const imgSrc = getImageSrc(src);

    if (!imgSrc || error) {
        return (
            <div style={{
                width: '100%', height: '180px',
                background: 'linear-gradient(135deg, #fff5f0, #ffe8e0)',
                display: 'flex', flexDirection: 'column',
                alignItems: 'center', justifyContent: 'center',
                borderRadius: '12px 12px 0 0'
            }}>
                <span style={{ fontSize: '48px' }}>🍽️</span>
                <span style={{ fontSize: '12px', color: '#999', marginTop: '8px' }}>
                    {name}
                </span>
            </div>
        );
    }

    return (
        <img
            src={imgSrc}
            alt={name}
            style={{
                width: '100%', height: '180px',
                objectFit: 'cover',
                borderRadius: '12px 12px 0 0'
            }}
            loading="lazy"
            onError={() => setError(true)}
        />
    );
};

const RestaurantCard = ({ restaurant, index }) => {
    const { token } = useAuth();
    const [isFav, setIsFav] = useState(restaurant.is_favourite);

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

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: index * 0.1 }}
            className="relative"
        >
            <Link to={`/client/restaurants/${restaurant.id}`} className="block group">
                <div className={`rounded-2xl overflow-hidden shadow-sm hover:shadow-2xl transition-all duration-500 bg-white border border-gray-100 h-full`}>
                    <div className="h-52 w-full relative group-hover:scale-105 transition-transform duration-700 flex items-center justify-center overflow-hidden">
                        <RestaurantImage src={restaurant.image_url} name={restaurant.name} />

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
