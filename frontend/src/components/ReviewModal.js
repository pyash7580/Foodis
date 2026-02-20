import React, { useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { toast } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';

import { useAuth } from '../contexts/AuthContext';

const StarRating = ({ rating, setRating, size = "md" }) => {
    return (
        <div className="flex space-x-1">
            {[1, 2, 3, 4, 5].map((star) => (
                <button
                    key={star}
                    type="button"
                    onClick={() => setRating(star)}
                    className={`${size === "lg" ? "text-3xl" : "text-xl"} focus:outline-none transition-transform transform hover:scale-110 ${star <= rating ? 'text-yellow-400' : 'text-gray-300'
                        }`}
                >
                    ★
                </button>
            ))}
        </div>
    );
};

const ReviewModal = ({ isOpen, onClose, order, onReviewSubmitted }) => {
    const { token } = useAuth();
    const [step, setStep] = useState(1); // 1: Restaurant, 2: Rider
    const [restaurantRating, setRestaurantRating] = useState(5);
    const [restaurantComment, setRestaurantComment] = useState('');
    const [riderRating, setRiderRating] = useState(5);
    const [riderComment, setRiderComment] = useState('');
    const [loading, setLoading] = useState(false);

    if (!isOpen) return null;

    const handleSubmitRestaurant = async () => {
        setLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/api/client/reviews/`, {
                restaurant: order.restaurant.id,
                order: order.id,
                rating: restaurantRating,
                comment: restaurantComment,
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });
            toast.success("Restaurant review submitted!");
            setStep(2); // Move to Rider Review
        } catch (error) {
            console.error("Restaurant review error:", error.response?.data || error);
            const errorMsg = error.response?.data?.detail
                || error.response?.data?.error
                || error.response?.data?.message
                || JSON.stringify(error.response?.data)
                || "Failed to submit restaurant review.";
            toast.error(errorMsg);
        } finally {
            setLoading(false);
        }
    };


    const handleSubmitRider = async () => {
        setLoading(true);
        try {
            if (order.rider) {
                // Use client endpoint for submitting rider reviews
                await axios.post(`${API_BASE_URL}/api/client/rider-reviews/`, {
                    rider: order.rider.id,
                    order: order.id,
                    rating: riderRating,
                    comment: riderComment,
                }, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                toast.success("Rider review submitted!");
            }
            onClose();
            if (onReviewSubmitted) onReviewSubmitted();
        } catch (error) {
            console.error("Rider review error:", error.response?.data || error);
            const errorMsg = error.response?.data?.detail
                || error.response?.data?.error
                || error.response?.data?.message
                || JSON.stringify(error.response?.data)
                || "Failed to submit rider review.";
            toast.error(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[2000] flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        className="bg-white rounded-3xl p-8 max-w-md w-full shadow-2xl relative overflow-hidden"
                    >
                        <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-red-500 to-orange-500"></div>

                        <h2 className="text-2xl font-black text-gray-800 mb-2 text-center">
                            {step === 1 ? "How was the food?" : "How was the delivery?"}
                        </h2>
                        <p className="text-center text-gray-500 mb-6 text-sm">
                            {step === 1 ? `Rate your experience with ${order.restaurant?.name}` : `Rate your delivery partner ${order.rider_name || ''}`}
                        </p>

                        <div className="flex justify-center mb-6">
                            <StarRating
                                rating={step === 1 ? restaurantRating : riderRating}
                                setRating={step === 1 ? setRestaurantRating : setRiderRating}
                                size="lg"
                            />
                        </div>

                        <textarea
                            className="w-full p-4 bg-gray-50 rounded-xl border border-gray-100 focus:border-red-500 focus:ring-0 transition mb-6 resize-none text-sm"
                            rows="4"
                            placeholder={step === 1 ? "Tell us about the taste, portion, etc." : "Was the delivery on time? Polite behavior?"}
                            value={step === 1 ? restaurantComment : riderComment}
                            onChange={(e) => step === 1 ? setRestaurantComment(e.target.value) : setRiderComment(e.target.value)}
                        ></textarea>

                        <div className="flex space-x-3">
                            {step === 1 && (
                                <button
                                    onClick={onClose} // Allow skipping
                                    className="flex-1 py-3 rounded-xl font-bold text-gray-400 hover:text-gray-600 hover:bg-gray-50 transition"
                                >
                                    Skip
                                </button>
                            )}
                            <button
                                onClick={step === 1 ? handleSubmitRestaurant : handleSubmitRider}
                                disabled={loading}
                                className="flex-1 py-3 bg-red-600 text-white rounded-xl font-bold hover:shadow-lg hover:shadow-red-500/30 transition transform active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed"
                            >
                                {loading ? 'Submitting...' : step === 1 ? 'Next' : 'Submit Review'}
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};

export default ReviewModal;
