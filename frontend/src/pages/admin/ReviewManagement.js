import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../config';
import toast from 'react-hot-toast';
import { FaSearch, FaStar, FaTrash, FaUser, FaStore } from 'react-icons/fa';
import { format } from 'date-fns';

const ReviewManagement = () => {
    const [reviews, setReviews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterRating, setFilterRating] = useState('ALL');

    useEffect(() => {
        fetchReviews();
    }, []);

    const fetchReviews = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token_admin');
            const res = await axios.get(`${API_BASE_URL}/api/admin/reviews/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' }
            });
            setReviews(res.data.results || res.data);
        } catch (error) {
            console.error("Failed to fetch reviews", error);
            toast.error("Failed to load reviews");
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Are you sure you want to delete this review?")) return;
        try {
            const token = localStorage.getItem('token_admin');
            await axios.delete(`${API_BASE_URL}/api/admin/reviews/${id}/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' }
            });
            toast.success("Review deleted successfully");
            fetchReviews();
        } catch (error) {
            toast.error("Failed to delete review");
        }
    };

    const filteredReviews = reviews.filter(review => {
        const matchesSearch =
            (review.user_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                review.restaurant_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                review.comment?.toLowerCase().includes(searchTerm.toLowerCase()));

        const matchesRating = filterRating === 'ALL' || review.rating.toString() === filterRating;

        return matchesSearch && matchesRating;
    });

    const renderStars = (rating) => {
        return [...Array(5)].map((_, i) => (
            <FaStar key={i} className={i < rating ? "text-yellow-400" : "text-gray-300"} />
        ));
    };

    if (loading) return <div className="p-8 text-center text-gray-500 font-bold">Loading Reviews...</div>;

    return (
        <div className="space-y-6">
            {/* Controls */}
            <div className="flex flex-col md:flex-row justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-gray-100 gap-4">
                <div className="relative w-full md:w-96">
                    <FaSearch className="absolute top-3.5 left-4 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search Review, User, Restaurant..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-12 pr-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-red-500"
                    />
                </div>

                <div className="flex items-center space-x-2">
                    <span className="text-gray-400 text-sm font-bold">Rating:</span>
                    <select
                        value={filterRating}
                        onChange={(e) => setFilterRating(e.target.value)}
                        className="p-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 bg-white"
                    >
                        <option value="ALL">All Ratings</option>
                        <option value="5">5 Stars</option>
                        <option value="4">4 Stars</option>
                        <option value="3">3 Stars</option>
                        <option value="2">2 Stars</option>
                        <option value="1">1 Star</option>
                    </select>
                </div>
            </div>

            {/* Reviews List */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredReviews.length > 0 ? (
                    filteredReviews.map(review => (
                        <div key={review.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between hover:shadow-md transition">
                            <div>
                                <div className="flex justify-between items-start mb-4">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center text-gray-500">
                                            <FaUser />
                                        </div>
                                        <div>
                                            <p className="font-bold text-gray-800 text-sm">{review.user_name || 'Anonymous'}</p>
                                            <p className="text-xs text-gray-400">{format(new Date(review.created_at), 'MMM dd, yyyy')}</p>
                                        </div>
                                    </div>
                                    <div className="flex text-yellow-400 text-sm">
                                        {renderStars(review.rating)}
                                    </div>
                                </div>

                                <div className="mb-4">
                                    <div className="flex items-center text-xs text-gray-500 mb-2 font-bold">
                                        <FaStore className="mr-1" /> {review.restaurant_name}
                                    </div>
                                    <p className="text-gray-600 text-sm italic">"{review.comment}"</p>
                                </div>
                            </div>

                            <div className="pt-4 border-t border-gray-50 flex justify-end">
                                <button
                                    onClick={() => handleDelete(review.id)}
                                    className="text-red-400 hover:text-red-600 p-2 rounded-lg hover:bg-red-50 transition"
                                    title="Delete Review"
                                >
                                    <FaTrash />
                                </button>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="col-span-full py-12 text-center text-gray-400">
                        No reviews found matching your criteria.
                    </div>
                )}
            </div>
        </div>
    );
};

export default ReviewManagement;
