import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../config';
import toast from 'react-hot-toast';
import { FaStore, FaTimes, FaCamera } from 'react-icons/fa';

const EditRestaurantModal = ({ restaurant, isOpen, onClose, onUpdate }) => {
    const [formData, setFormData] = useState({
        name: '',
        phone: '',
        email: '',
        cuisine: '',
        description: '',
        address: '',
        city: '',
        state: '',
        pincode: '',
        delivery_time: 30,
        delivery_fee: 0,
        min_order_amount: 0,
        commission_rate: 15,
        is_veg: false
    });

    // Separate state for files
    const [imageFile, setImageFile] = useState(null);
    const [coverImageFile, setCoverImageFile] = useState(null);

    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        if (restaurant) {
            setFormData({
                name: restaurant.name || '',
                phone: restaurant.phone || '',
                email: restaurant.email || '',
                cuisine: restaurant.cuisine || '',
                description: restaurant.description || '',
                address: restaurant.address || '',
                city: restaurant.city || '',
                state: restaurant.state || '',
                pincode: restaurant.pincode || '',
                delivery_time: restaurant.delivery_time || 30,
                delivery_fee: restaurant.delivery_fee || 0,
                min_order_amount: restaurant.min_order_amount || 0,
                commission_rate: restaurant.commission_rate || 15,
                is_veg: restaurant.is_veg || false
            });
            setImageFile(null);
            setCoverImageFile(null);
        }
    }, [restaurant]);

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleFileChange = (e) => {
        const { name, files } = e.target;
        if (files && files[0]) {
            if (name === 'image') setImageFile(files[0]);
            if (name === 'cover_image') setCoverImageFile(files[0]);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);

        try {
            const token = localStorage.getItem('token_admin');
            const data = new FormData();

            // Append text fields
            Object.keys(formData).forEach(key => {
                data.append(key, formData[key]);
            });

            // Append files if selected
            if (imageFile) data.append('image', imageFile);
            if (coverImageFile) data.append('cover_image', coverImageFile);

            const response = await axios.patch(
                `${API_BASE_URL}/api/admin/restaurants/${restaurant.id}/`,
                data,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'X-Role': 'ADMIN',
                        'Content-Type': 'multipart/form-data'
                    }
                }
            );

            toast.success('Restaurant updated successfully');
            onUpdate(response.data);
            onClose();
        } catch (error) {
            console.error('Failed to update restaurant', error);
            const errorMsg = error.response?.data?.error || 'Failed to update restaurant';
            toast.error(errorMsg);
        } finally {
            setSubmitting(false);
        }
    };

    if (!isOpen || !restaurant) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-center z-10">
                    <h2 className="text-2xl font-bold text-gray-800 flex items-center">
                        <FaStore className="mr-3 text-red-500" />
                        Edit Restaurant
                    </h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">
                        <FaTimes />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                    {/* Images Section */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-gray-700 border-b pb-2">Images</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Logo</label>
                                <div className="flex items-center space-x-4">
                                    <div className="w-20 h-20 bg-gray-100 rounded-lg overflow-hidden border">
                                        {imageFile ? (
                                            <img src={URL.createObjectURL(imageFile)} alt="Preview" className="w-full h-full object-cover" />
                                        ) : restaurant.image ? (
                                            <img src={restaurant.image} alt="Current" className="w-full h-full object-cover" />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center text-gray-400"><FaStore /></div>
                                        )}
                                    </div>
                                    <label className="cursor-pointer bg-gray-50 border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-100 transition">
                                        <div className="flex items-center space-x-2">
                                            <FaCamera />
                                            <span>Change Logo</span>
                                        </div>
                                        <input type="file" name="image" onChange={handleFileChange} accept="image/*" className="hidden" />
                                    </label>
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Cover Image</label>
                                <div className="flex items-center space-x-4">
                                    <div className="w-32 h-20 bg-gray-100 rounded-lg overflow-hidden border">
                                        {coverImageFile ? (
                                            <img src={URL.createObjectURL(coverImageFile)} alt="Preview" className="w-full h-full object-cover" />
                                        ) : restaurant.cover_image ? (
                                            <img src={restaurant.cover_image} alt="Current" className="w-full h-full object-cover" />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">No Cover</div>
                                        )}
                                    </div>
                                    <label className="cursor-pointer bg-gray-50 border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-100 transition">
                                        <div className="flex items-center space-x-2">
                                            <FaCamera />
                                            <span>Change Cover</span>
                                        </div>
                                        <input type="file" name="cover_image" onChange={handleFileChange} accept="image/*" className="hidden" />
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Basic Info */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-gray-700 border-b pb-2">Basic Info</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Restaurant Name</label>
                                <input
                                    type="text"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleInputChange}
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Cuisine</label>
                                <input
                                    type="text"
                                    name="cuisine"
                                    value={formData.cuisine}
                                    onChange={handleInputChange}
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                            <textarea
                                name="description"
                                value={formData.description}
                                onChange={handleInputChange}
                                rows="3"
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                            />
                        </div>
                    </div>

                    {/* Contact & Location */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-gray-700 border-b pb-2">Contact & Location</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                                <input
                                    type="text"
                                    name="phone"
                                    value={formData.phone}
                                    onChange={handleInputChange}
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleInputChange}
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                            <textarea
                                name="address"
                                value={formData.address}
                                onChange={handleInputChange}
                                rows="2"
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                            />
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                                <input
                                    type="text"
                                    name="city"
                                    value={formData.city}
                                    onChange={handleInputChange}
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
                                <input
                                    type="text"
                                    name="state"
                                    value={formData.state}
                                    onChange={handleInputChange}
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Pincode</label>
                                <input
                                    type="text"
                                    name="pincode"
                                    value={formData.pincode}
                                    onChange={handleInputChange}
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Settings */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-gray-700 border-b pb-2">Settings</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Delivery Time (mins)</label>
                                <input
                                    type="number"
                                    name="delivery_time"
                                    value={formData.delivery_time}
                                    onChange={handleInputChange}
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Delivery Fee (₹)</label>
                                <input
                                    type="number"
                                    name="delivery_fee"
                                    value={formData.delivery_fee}
                                    onChange={handleInputChange}
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Min Order (₹)</label>
                                <input
                                    type="number"
                                    name="min_order_amount"
                                    value={formData.min_order_amount}
                                    onChange={handleInputChange}
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Commission (%)</label>
                                <input
                                    type="number"
                                    name="commission_rate"
                                    value={formData.commission_rate}
                                    onChange={handleInputChange}
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                />
                            </div>
                        </div>
                        <div className="flex items-center">
                            <input
                                type="checkbox"
                                name="is_veg"
                                checked={formData.is_veg}
                                onChange={handleInputChange}
                                className="w-4 h-4 text-red-500 rounded focus:ring-red-500"
                            />
                            <label className="ml-2 text-sm font-medium text-gray-700">Pure Vegetarian</label>
                        </div>
                    </div>

                    <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-3 sm:space-x-3 pt-4 border-t">
                        <button
                            type="button"
                            onClick={onClose}
                            className="w-full sm:w-auto px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-semibold text-center"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={submitting}
                            className="w-full sm:w-auto px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 font-semibold disabled:opacity-50 text-center"
                        >
                            {submitting ? 'Updating...' : 'Save Changes'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default EditRestaurantModal;
