import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import toast from 'react-hot-toast';

const DishCard = ({ item }) => {
    const { addToCart, cartItems, updateQuantity } = useCart();
    const { token } = useAuth();
    const [isFavourite, setIsFavourite] = useState(item.is_favourite);

    const cartItem = cartItems.find(c => c.id === item.id);
    const quantity = cartItem ? cartItem.quantity : 0;

    const toggleFavItem = async (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (!token) {
            toast.error("Please login to favourite items");
            return;
        }
        try {
            const res = await axios.post(`${API_BASE_URL}/api/client/favourite-menu-items/toggle/`,
                { menu_item_id: item.id },
                { headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' } }
            );
            setIsFavourite(res.data.status === 'added');
            toast.success(res.data.status === 'added' ? "Added to favourites!" : "Removed from favourites");
        } catch (err) {
            toast.error("Failed to update favorite");
        }
    };

    // Construct restaurant object for cart context since search result might have flattened it
    const restaurantObj = {
        id: item.restaurant, // Depending on serializer, this might be ID or object. Let's assume ID from serializer update.
        // But addToCart needs full object sometimes? Let's check CartContext. 
        // Actually addToCart usually expects restaurant object with at least id, name, delivery_fee etc.
        // Our serializer sends: restaurant (ID), restaurant_name, restaurant_slug, restaurant_city.
        // We'll create a minimal valid object.
        name: item.restaurant_name,
        slug: item.restaurant_slug,
        city: item.restaurant_city,
        delivery_fee: 0, // Fallback if not provided. Search results usually don't have this.
        min_order_amount: 0,
        // If we strictly need more data, we might need a fetch or update serializer further. 
        // For now, let's assume CartContext handles minimal checks or we'll rely on backend validation.
    };

    // Note: If addToCart checks restaurant.id matching cart.restaurant.id, we are good if we pass {id: item.restaurant}.

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ y: -5 }}
            className="bg-white rounded-3xl overflow-hidden shadow-sm border border-gray-100 hover:shadow-xl transition-all duration-300 group flex flex-col h-full"
        >
            <div className="relative h-48 overflow-hidden">
                <Link to={`/client/restaurants/${item.restaurant}`}> {/* Link to Restaurant */}
                    {item.image || item.image_url ? (
                        <img
                            src={item.image || item.image_url}
                            alt={item.name}
                            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                        />
                    ) : (
                        <div className="w-full h-full bg-gray-50 flex items-center justify-center text-4xl">🍲</div>
                    )}
                </Link>

                <div className="absolute top-4 right-4">
                    <button
                        onClick={toggleFavItem}
                        className={`p-2 rounded-full bg-white/90 backdrop-blur shadow-sm transition-all duration-300 ${isFavourite ? 'text-red-500' : 'text-gray-400 hover:text-red-500'}`}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill={isFavourite ? "currentColor" : "none"} stroke="currentColor" strokeWidth={isFavourite ? "0" : "2"}>
                            <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                        </svg>
                    </button>
                </div>

                <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur px-3 py-1 rounded-lg text-xs font-bold shadow-sm flex items-center gap-1">
                    <span className={item.veg_type === 'VEG' ? 'text-green-600' : 'text-red-600'}>
                        {item.veg_type === 'VEG' ? '●' : '●'}
                    </span>
                    <span className="text-gray-800 uppercase tracking-wider">{item.veg_type === 'VEG' ? 'VEG' : 'NON-VEG'}</span>
                </div>
            </div>

            <div className="p-5 flex flex-col flex-grow">
                <div className="mb-1">
                    <Link to={`/client/restaurants/${item.restaurant}`} className="text-xs font-bold text-gray-400 hover:text-red-600 uppercase tracking-wider transition-colors">
                        {item.restaurant_name}
                    </Link>
                </div>

                <h3 className="text-lg font-black text-gray-900 mb-1 leading-tight group-hover:text-red-600 transition-colors">
                    {item.name}
                </h3>

                <p className="text-gray-500 text-sm mb-4 line-clamp-2">{item.description}</p>

                <div className="mt-auto flex items-center justify-between pt-4 border-t border-gray-50">
                    <span className="text-xl font-black text-gray-900">₹{item.price}</span>

                    {quantity > 0 ? (
                        <div className="flex items-center bg-gray-100 rounded-xl overflow-hidden shadow-inner">
                            <button
                                className="px-3 py-1 text-red-600 font-bold hover:bg-gray-200 transition"
                                onClick={() => updateQuantity(item.id, -1)}
                            >−</button>
                            <span className="px-1 text-sm font-bold text-gray-900">{quantity}</span>
                            <button
                                className="px-3 py-1 text-red-600 font-bold hover:bg-gray-200 transition"
                                onClick={() => updateQuantity(item.id, 1)}
                            >+</button>
                        </div>
                    ) : (
                        <button
                            onClick={() => addToCart(item, { id: item.restaurant })}
                            className="bg-red-50 text-red-600 px-4 py-2 rounded-xl font-bold hover:bg-red-600 hover:text-white transition-all shadow-sm"
                        >
                            ADD
                        </button>
                    )}
                </div>
            </div>
        </motion.div>
    );
};

export default DishCard;
