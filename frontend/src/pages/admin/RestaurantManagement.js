
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../config';
import toast from 'react-hot-toast';
import { FaSearch, FaFilter, FaStore, FaEye, FaCheckCircle, FaBan, FaTimesCircle, FaMapMarkerAlt, FaStar, FaPlus, FaCopy, FaTrash } from 'react-icons/fa';
import RestaurantDetails from './RestaurantDetails';


const RestaurantManagement = () => {
    const [restaurants, setRestaurants] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('PENDING'); // Default to PENDING
    const [selectedRestaurantId, setSelectedRestaurantId] = useState(null);


    // Add Restaurant Modal States
    const [showAddModal, setShowAddModal] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        create_owner_name: '',
        create_owner_phone: '',
        create_owner_email: '',
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

    // Success credentials modal
    const [showSuccessModal, setShowSuccessModal] = useState(false);
    const [createdCredentials, setCreatedCredentials] = useState(null);

    useEffect(() => {
        fetchRestaurants();
    }, []);

    const fetchRestaurants = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token_admin');
            const res = await axios.get(`${API_BASE_URL}/api/admin/restaurants/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' }
            });
            // Handle pagination if present
            const data = res.data.results ? res.data.results : res.data;

            if (Array.isArray(data)) {
                setRestaurants(data);
            } else {
                console.error("API response is not an array:", data);
                toast.error("Invalid data received");
            }
        } catch (error) {
            console.error("Failed to fetch restaurants", error);
            toast.error("Failed to load restaurants");
        } finally {
            setLoading(false);
        }
    };

    const handleAction = async (restaurantId, action) => {
        // action: 'approve', 'reject', 'suspend'
        if (!window.confirm(`Are you sure you want to ${action.toUpperCase()} this restaurant?`)) return;

        try {
            const token = localStorage.getItem('token_admin');
            await axios.post(`${API_BASE_URL}/api/admin/restaurants/${restaurantId}/${action}/`, {}, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' }
            });
            toast.success(`Restaurant ${action}d successfully`);
            fetchRestaurants(); // Refresh list
        } catch (error) {
            console.error(`Failed to ${action} restaurant`, error);
            toast.error(`Failed to ${action} restaurant`);
        }
    };



    const handleDelete = async (restaurantId, restaurantName) => {

        if (!window.confirm(`⚠️ WARNING: This will permanently delete "${restaurantName}" and its owner account. This action CANNOT be undone!\n\nAre you absolutely sure you want to DELETE this restaurant?`)) return;

        try {
            const token = localStorage.getItem('token_admin');
            await axios.delete(`${API_BASE_URL}/api/admin/restaurants/${restaurantId}/delete_restaurant/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' }
            });
            toast.success('Restaurant deleted permanently');
            fetchRestaurants(); // Refresh list
        } catch (error) {
            console.error('Failed to delete restaurant', error);
            const errorMsg = error.response?.data?.error || 'Failed to delete restaurant';
            toast.error(errorMsg);
        }
    };

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const resetForm = () => {
        setFormData({
            name: '',
            create_owner_name: '',
            create_owner_phone: '',
            create_owner_email: '',
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
    };

    const handleAddRestaurant = async (e) => {
        e.preventDefault();

        // Validate required fields
        if (!formData.name || !formData.create_owner_phone || !formData.phone ||
            !formData.address || !formData.city || !formData.state || !formData.pincode) {
            toast.error('Please fill in all required fields');
            return;
        }

        setSubmitting(true);
        try {
            const token = localStorage.getItem('token_admin');
            const response = await axios.post(
                `${API_BASE_URL}/api/admin/restaurants/`,
                formData,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'X-Role': 'ADMIN',
                        'Content-Type': 'application/json'
                    }
                }
            );

            // Store credentials for success modal
            setCreatedCredentials({
                name: response.data.name,
                phone: response.data.owner_phone,
                password: response.data.generated_password
            });

            toast.success('Restaurant created successfully!');
            setShowAddModal(false);
            setShowSuccessModal(true);
            resetForm();
            fetchRestaurants(); // Refresh list
        } catch (error) {
            console.error('Failed to create restaurant', error);
            console.error('Error response:', error.response?.data);

            // Extract detailed error message
            let errorMsg = 'Failed to create restaurant';
            if (error.response?.data) {
                if (error.response.data.error) {
                    errorMsg = error.response.data.error;
                } else if (typeof error.response.data === 'object') {
                    // If validation errors, show first error
                    const firstError = Object.values(error.response.data)[0];
                    if (Array.isArray(firstError)) {
                        errorMsg = firstError[0];
                    } else if (typeof firstError === 'string') {
                        errorMsg = firstError;
                    }
                }
            }
            toast.error(errorMsg);
        } finally {
            setSubmitting(false);
        }
    };

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        toast.success('Copied to clipboard!');
    };

    // Filtering logic
    const filteredRestaurants = restaurants.filter(restaurant => {
        // Exclude REJECTED restaurants from the list entirely
        if (restaurant.status === 'REJECTED') {
            return false;
        }

        const matchesSearch =
            (restaurant.name?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
            (restaurant.owner_name?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
            (restaurant.phone?.includes(searchTerm)) ||
            (restaurant.city?.toLowerCase() || '').includes(searchTerm.toLowerCase());

        // Filter by selected status
        const matchesStatus = restaurant.status === filterStatus;

        return matchesSearch && matchesStatus;
    });

    if (loading) return <div className="p-8 text-center text-gray-500 font-bold">Loading Restaurants...</div>;

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-gray-800 flex items-center">
                <FaStore className="mr-3 text-red-500" />
                Restaurant Management
            </h1>

            {/* Header & Controls */}
            <div className="flex flex-col md:flex-row justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-gray-100 gap-4">
                <div className="relative w-full md:w-96">
                    <FaSearch className="absolute top-3.5 left-4 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search Restaurant, Owner, City..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-12 pr-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-red-500"
                    />
                </div>

                <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
                    <div className="flex items-center space-x-2 flex-grow sm:flex-grow-0">
                        <FaFilter className="text-gray-400" />
                        <select
                            value={filterStatus}
                            onChange={(e) => setFilterStatus(e.target.value)}
                            className="p-3 border border-gray-200 rounded-lg focus:outline-none w-full sm:w-auto"
                        >
                            <option value="PENDING">Approval</option>
                            <option value="APPROVED">Approved</option>
                            <option value="SUSPENDED">Suspended</option>
                        </select>
                    </div>

                    <button
                        onClick={() => setShowAddModal(true)}
                        className="flex items-center justify-center space-x-2 px-4 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition font-semibold w-full sm:w-auto"
                    >
                        <FaPlus />
                        <span>Add New Restaurant</span>
                    </button>
                </div>
            </div>

            {/* Restaurants Table */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm text-gray-600">
                        <thead className="bg-gray-50 text-gray-800 uppercase tracking-wider font-bold">
                            <tr>
                                <th className="p-4">Restaurant</th>
                                <th className="p-4">Owner Info</th>

                                <th className="p-4">Location</th>
                                <th className="p-4 text-center">Status</th>
                                <th className="p-4 text-center">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {filteredRestaurants.length > 0 ? (
                                filteredRestaurants.map(restaurant => (
                                    <tr key={restaurant.id} className="hover:bg-gray-50 transition">
                                        <td className="p-4">
                                            <div className="flex items-center space-x-3">
                                                <div className="w-10 h-10 bg-gray-200 rounded-lg flex-shrink-0 overflow-hidden">
                                                    {restaurant.image ? (
                                                        <img src={restaurant.image} alt="" className="w-full h-full object-cover" />
                                                    ) : (
                                                        <div className="w-full h-full flex items-center justify-center text-gray-400"><FaStore /></div>
                                                    )}
                                                </div>
                                                <div>
                                                    <p className="font-bold text-gray-800">{restaurant.name}</p>
                                                    <div className="flex items-center text-xs text-yellow-500 font-bold">
                                                        <FaStar className="mr-1" /> {restaurant.rating || 'New'}
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="p-4">
                                            <p className="font-medium text-gray-800">{restaurant.owner_name}</p>
                                            <p className="text-xs text-gray-400">{restaurant.owner_phone || restaurant.phone}</p>
                                        </td>

                                        <td className="p-4">
                                            <div className="flex items-center text-gray-500">
                                                <FaMapMarkerAlt className="mr-1 text-gray-300" />
                                                <span className="truncate max-w-[150px]" title={`${restaurant.address}, ${restaurant.city}`}>
                                                    {restaurant.city}, {restaurant.state}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="p-4 text-center">
                                            <span className={`px-3 py-1 rounded-full text-xs font-bold ${restaurant.status === 'APPROVED' ? 'bg-green-100 text-green-700' :
                                                restaurant.status === 'PENDING' ? 'bg-yellow-100 text-yellow-700' :
                                                    'bg-red-100 text-red-700'
                                                }`}>
                                                {restaurant.status === 'PENDING' ? 'APPROVAL' : restaurant.status}
                                            </span>
                                        </td>
                                        <td className="p-4 text-center">
                                            <div className="flex items-center justify-center space-x-2">
                                                <button
                                                    onClick={() => setSelectedRestaurantId(restaurant.id)}

                                                    className="p-2 bg-blue-50 text-blue-500 rounded-lg hover:bg-blue-100 transition"
                                                    title="View Details"
                                                >
                                                    <FaEye />
                                                </button>

                                                {restaurant.status === 'PENDING' && (
                                                    <>
                                                        <button
                                                            onClick={() => handleAction(restaurant.id, 'approve')}
                                                            className="p-2 bg-green-50 text-green-500 rounded-lg hover:bg-green-100"
                                                            title="Approve"
                                                        >
                                                            <FaCheckCircle />
                                                        </button>
                                                        <button
                                                            onClick={() => handleAction(restaurant.id, 'reject')}
                                                            className="p-2 bg-red-50 text-red-500 rounded-lg hover:bg-red-100"
                                                            title="Reject"
                                                        >
                                                            <FaTimesCircle />
                                                        </button>
                                                    </>
                                                )}

                                                {restaurant.status === 'APPROVED' && (
                                                    <button
                                                        onClick={() => handleAction(restaurant.id, 'suspend')}
                                                        className="p-2 bg-red-50 text-red-500 rounded-lg hover:bg-red-100"
                                                        title="Suspend"
                                                    >
                                                        <FaBan />
                                                    </button>
                                                )}
                                                {restaurant.status === 'SUSPENDED' && (
                                                    <button
                                                        onClick={() => handleAction(restaurant.id, 'approve')}
                                                        className="p-2 bg-green-50 text-green-500 rounded-lg hover:bg-green-100"
                                                        title="Re-activate"
                                                    >
                                                        <FaCheckCircle />
                                                    </button>
                                                )}

                                                {/* Delete button - always visible */}
                                                <button
                                                    onClick={() => handleDelete(restaurant.id, restaurant.name)}
                                                    className="p-2 bg-gray-50 text-gray-600 rounded-lg hover:bg-red-50 hover:text-red-600 transition"
                                                    title="Delete Permanently"
                                                >
                                                    <FaTrash />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="5" className="p-8 text-center text-gray-400">
                                        No restaurants found.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {selectedRestaurantId && (
                <RestaurantDetails
                    restaurantId={selectedRestaurantId}
                    onClose={() => setSelectedRestaurantId(null)}
                />
            )}



            {/* Add Restaurant Modal */}

            {showAddModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-center">
                            <h2 className="text-2xl font-bold text-gray-800 flex items-center">
                                <FaStore className="mr-3 text-red-500" />
                                Add New Restaurant
                            </h2>
                            <button
                                onClick={() => { setShowAddModal(false); resetForm(); }}
                                className="text-gray-400 hover:text-gray-600 text-2xl"
                            >
                                ×
                            </button>
                        </div>

                        <form onSubmit={handleAddRestaurant} className="p-6 space-y-6">
                            {/* Restaurant Details */}
                            <div className="space-y-4">
                                <h3 className="text-lg font-semibold text-gray-700 border-b pb-2">Restaurant Details</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Restaurant Name <span className="text-red-500">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            name="name"
                                            value={formData.name}
                                            onChange={handleInputChange}
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Cuisine Type</label>
                                        <input
                                            type="text"
                                            name="cuisine"
                                            value={formData.cuisine}
                                            onChange={handleInputChange}
                                            placeholder="e.g., Indian, Chinese, Italian"
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

                            {/* Owner Details */}
                            <div className="space-y-4">
                                <h3 className="text-lg font-semibold text-gray-700 border-b pb-2">Owner Details</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Owner Name <span className="text-red-500">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            name="create_owner_name"
                                            value={formData.create_owner_name}
                                            onChange={handleInputChange}
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Owner Phone <span className="text-red-500">*</span>
                                        </label>
                                        <input
                                            type="tel"
                                            name="create_owner_phone"
                                            value={formData.create_owner_phone}
                                            onChange={handleInputChange}
                                            placeholder="10-digit mobile number"
                                            maxLength="10"
                                            minLength="10"
                                            pattern="[0-9]{10}"
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Owner Email</label>
                                        <input
                                            type="email"
                                            name="create_owner_email"
                                            value={formData.create_owner_email}
                                            onChange={handleInputChange}
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Contact Details */}
                            <div className="space-y-4">
                                <h3 className="text-lg font-semibold text-gray-700 border-b pb-2">Contact Information</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Restaurant Phone <span className="text-red-500">*</span>
                                        </label>
                                        <input
                                            type="tel"
                                            name="phone"
                                            value={formData.phone}
                                            onChange={handleInputChange}
                                            placeholder="10-digit phone number"
                                            maxLength="10"
                                            minLength="10"
                                            pattern="[0-9]{10}"
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Restaurant Email</label>
                                        <input
                                            type="email"
                                            name="email"
                                            value={formData.email}
                                            onChange={handleInputChange}
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Address */}
                            <div className="space-y-4">
                                <h3 className="text-lg font-semibold text-gray-700 border-b pb-2">Address</h3>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Full Address <span className="text-red-500">*</span>
                                    </label>
                                    <textarea
                                        name="address"
                                        value={formData.address}
                                        onChange={handleInputChange}
                                        rows="2"
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                        required
                                    />
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            City <span className="text-red-500">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            name="city"
                                            value={formData.city}
                                            onChange={handleInputChange}
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            State <span className="text-red-500">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            name="state"
                                            value={formData.state}
                                            onChange={handleInputChange}
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Pincode <span className="text-red-500">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            name="pincode"
                                            value={formData.pincode}
                                            onChange={handleInputChange}
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                            required
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Business Settings */}
                            <div className="space-y-4">
                                <h3 className="text-lg font-semibold text-gray-700 border-b pb-2">Business Settings</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Delivery Time (minutes)</label>
                                        <input
                                            type="number"
                                            name="delivery_time"
                                            value={formData.delivery_time}
                                            onChange={handleInputChange}
                                            min="0"
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Delivery Fee (₹)</label>
                                        <input
                                            type="number"
                                            step="0.01"
                                            name="delivery_fee"
                                            value={formData.delivery_fee}
                                            onChange={handleInputChange}
                                            min="0"
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Min Order Amount (₹)</label>
                                        <input
                                            type="number"
                                            step="0.01"
                                            name="min_order_amount"
                                            value={formData.min_order_amount}
                                            onChange={handleInputChange}
                                            min="0"
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Commission Rate (%)</label>
                                        <input
                                            type="number"
                                            step="0.01"
                                            name="commission_rate"
                                            value={formData.commission_rate}
                                            onChange={handleInputChange}
                                            min="0"
                                            max="100"
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
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
                                    <label className="ml-2 text-sm font-medium text-gray-700">Pure Vegetarian Restaurant</label>
                                </div>
                            </div>

                            {/* Submit Buttons */}
                            <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-3 sm:space-x-3 pt-4 border-t">
                                <button
                                    type="button"
                                    onClick={() => { setShowAddModal(false); resetForm(); }}
                                    className="w-full sm:w-auto px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-semibold"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={submitting}
                                    className="w-full sm:w-auto px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {submitting ? 'Creating...' : 'Create Restaurant'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Success Credentials Modal */}
            {showSuccessModal && createdCredentials && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-xl max-w-md w-full p-6">
                        <div className="text-center">
                            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-4">
                                <FaCheckCircle className="h-10 w-10 text-green-600" />
                            </div>
                            <h3 className="text-xl font-bold text-gray-900 mb-2">Restaurant Created Successfully!</h3>
                            <p className="text-sm text-gray-600 mb-6">
                                Please share these login credentials with the restaurant owner.
                            </p>

                            <div className="bg-gray-50 rounded-lg p-4 space-y-3 text-left">
                                <div>
                                    <label className="text-xs font-semibold text-gray-500 uppercase">Restaurant Name</label>
                                    <p className="text-gray-800 font-semibold">{createdCredentials.name}</p>
                                </div>
                                <div>
                                    <label className="text-xs font-semibold text-gray-500 uppercase">Login Phone</label>
                                    <div className="flex items-center justify-between">
                                        <p className="text-gray-800 font-mono">{createdCredentials.phone}</p>
                                        <button
                                            onClick={() => copyToClipboard(createdCredentials.phone)}
                                            className="text-blue-500 hover:text-blue-700"
                                        >
                                            <FaCopy />
                                        </button>
                                    </div>
                                </div>
                                <div>
                                    <label className="text-xs font-semibold text-gray-500 uppercase">Password</label>
                                    <div className="flex items-center justify-between">
                                        <p className="text-gray-800 font-mono">{createdCredentials.password}</p>
                                        <button
                                            onClick={() => copyToClipboard(createdCredentials.password)}
                                            className="text-blue-500 hover:text-blue-700"
                                        >
                                            <FaCopy />
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div className="mt-6">
                                <button
                                    onClick={() => { setShowSuccessModal(false); setCreatedCredentials(null); }}
                                    className="w-full px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 font-semibold"
                                >
                                    Close
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RestaurantManagement;
