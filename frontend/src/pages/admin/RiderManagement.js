
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../config';
import toast from 'react-hot-toast';
import { FaSearch, FaFilter, FaMotorcycle, FaBicycle, FaEye, FaCheckCircle, FaBan, FaTimesCircle, FaStar, FaIdCard, FaPlus, FaTimes } from 'react-icons/fa';
import RiderDetails from './RiderDetails';

const RiderManagement = () => {
    const [riders, setRiders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('ALL'); // ALL, PENDING, APPROVED, REJECTED, SUSPENDED
    const [selectedRiderId, setSelectedRiderId] = useState(null);
    const [showAddModal, setShowAddModal] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        phone: '',
        vehicle_number: '',
        license_number: '',
        account_holder_name: '',
        account_number: '',
        ifsc_code: '',
        bank_name: '',
        city: 'Mehsana',
        status: 'APPROVED'
    });

    useEffect(() => {
        fetchRiders();
    }, []);

    const fetchRiders = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token_admin');
            const res = await axios.get(`${API_BASE_URL}/api/admin/riders/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' }
            });
            // Handle pagination if present
            const data = res.data.results ? res.data.results : res.data;

            if (Array.isArray(data)) {
                setRiders(data);
            } else {
                console.error("API response is not an array:", data);
                toast.error("Invalid data received");
            }
        } catch (error) {
            console.error("Failed to fetch riders", error);
            toast.error("Failed to load riders");
        } finally {
            setLoading(false);
        }
    };

    const handleAction = async (riderId, action) => {
        // action: 'approve', 'reject', 'suspend'
        if (!window.confirm(`Are you sure you want to ${action.toUpperCase()} this rider?`)) return;

        try {
            const token = localStorage.getItem('token_admin');
            await axios.post(`${API_BASE_URL}/api/admin/riders/${riderId}/${action}/`, {}, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' }
            });
            toast.success(`Rider ${action}d successfully`);
            fetchRiders(); // Refresh list
        } catch (error) {
            console.error(`Failed to ${action} rider`, error);
            toast.error(`Failed to ${action} rider`);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const resetForm = () => {
        setFormData({
            name: '',
            email: '',
            password: '',
            phone: '',
            vehicle_number: '',
            license_number: '',
            account_holder_name: '',
            account_number: '',
            ifsc_code: '',
            bank_name: '',
            city: 'Mehsana',
            status: 'APPROVED'
        });
    };

    const handleAddRider = async (e) => {
        e.preventDefault();

        // Validation
        if (!formData.name || !formData.password || !formData.phone) {
            toast.error('Please fill in all required fields (Name, Password, Phone)');
            return;
        }

        if (formData.phone.length !== 10 || !/^\d+$/.test(formData.phone)) {
            toast.error('Phone must be exactly 10 digits');
            return;
        }

        setSubmitting(true);
        try {
            const token = localStorage.getItem('token_admin');
            await axios.post(`${API_BASE_URL}/api/admin/riders/`, formData, {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'X-Role': 'ADMIN'
                }
            });
            toast.success('Rider created successfully!');
            setShowAddModal(false);
            resetForm();
            fetchRiders(); // Refresh list
        } catch (error) {
            console.error('Failed to create rider', error);
            console.error('Error response:', error.response?.data);

            // Extract detailed error message
            let errorMsg = 'Failed to create rider';
            if (error.response?.data) {
                if (error.response.data.error) {
                    errorMsg = error.response.data.error;
                } else if (typeof error.response.data === 'object') {
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

    // Filtering logic
    const filteredRiders = riders.filter(rider => {
        const matchesSearch =
            (rider.rider_name?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
            (rider.rider_phone?.includes(searchTerm)) ||
            (rider.vehicle_number?.toLowerCase() || '').includes(searchTerm.toLowerCase());

        const matchesStatus =
            filterStatus === 'ALL' ? true : rider.status === filterStatus;

        return matchesSearch && matchesStatus;
    });

    if (loading) return <div className="p-8 text-center text-gray-500 font-bold">Loading Riders...</div>;

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-gray-800 flex items-center">
                <FaMotorcycle className="mr-3 text-red-500" />
                Rider Management
            </h1>

            {/* Header & Controls */}
            <div className="flex flex-col md:flex-row justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-gray-100 gap-4">
                <div className="relative w-full md:w-96">
                    <FaSearch className="absolute top-3.5 left-4 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search Name, Phone, Vehicle..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-12 pr-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-red-500"
                    />
                </div>

                <div className="flex items-center space-x-2">
                    <FaFilter className="text-gray-400" />
                    <select
                        value={filterStatus}
                        onChange={(e) => setFilterStatus(e.target.value)}
                        className="p-3 border border-gray-200 rounded-lg focus:outline-none"
                    >
                        <option value="ALL">All Status</option>
                        <option value="APPROVED">Approved</option>
                    </select>
                </div>

                <button
                    onClick={() => setShowAddModal(true)}
                    className="flex items-center px-4 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition font-bold"
                >
                    <FaPlus className="mr-2" />
                    Add New Rider
                </button>
            </div>

            {/* Riders Table */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm text-gray-600">
                        <thead className="bg-gray-50 text-gray-800 uppercase tracking-wider font-bold">
                            <tr>
                                <th className="p-4">Rider</th>
                                <th className="p-4">Contact</th>
                                <th className="p-4">Vehicle Info</th>
                                <th className="p-4 text-center">Status</th>
                                <th className="p-4 text-center">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {filteredRiders.length > 0 ? (
                                filteredRiders.map(rider => (
                                    <tr key={rider.id} className="hover:bg-gray-50 transition">
                                        <td className="p-4">
                                            <div className="flex items-center space-x-3">
                                                <div className="w-10 h-10 bg-gray-100 rounded-lg flex-shrink-0 flex items-center justify-center text-gray-400">
                                                    <FaMotorcycle />
                                                </div>
                                                <div>
                                                    <p className="font-bold text-gray-800">{rider.rider_name}</p>
                                                    <div className="flex items-center text-xs text-yellow-500 font-bold">
                                                        <FaStar className="mr-1" /> {rider.rating || 'New'}
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="p-4">
                                            <p className="font-medium text-gray-800">{rider.rider_phone}</p>
                                            <p className="text-xs text-gray-400">{rider.rider_email}</p>
                                        </td>
                                        <td className="p-4">
                                            <div className="flex flex-col">
                                                <span className="font-bold text-gray-700">{rider.vehicle_number}</span>
                                                <span className="text-xs text-gray-500 uppercase">{rider.vehicle_type}</span>
                                            </div>
                                        </td>
                                        <td className="p-4 text-center">
                                            <span className={`px-3 py-1 rounded-full text-xs font-bold ${rider.status === 'APPROVED' ? 'bg-green-100 text-green-700' :
                                                rider.status === 'PENDING' ? 'bg-yellow-100 text-yellow-700' :
                                                    'bg-red-100 text-red-700'
                                                }`}>
                                                {rider.status}
                                            </span>
                                        </td>
                                        <td className="p-4 text-center">
                                            <div className="flex items-center justify-center space-x-2">
                                                <button
                                                    onClick={() => setSelectedRiderId(rider.id)}
                                                    className="p-2 bg-blue-50 text-blue-500 rounded-lg hover:bg-blue-100 transition"
                                                    title="View Details"
                                                >
                                                    <FaEye />
                                                </button>

                                                {rider.status === 'PENDING' && (
                                                    <>
                                                        <button
                                                            onClick={() => handleAction(rider.id, 'approve')}
                                                            className="p-2 bg-green-50 text-green-500 rounded-lg hover:bg-green-100"
                                                            title="Approve"
                                                        >
                                                            <FaCheckCircle />
                                                        </button>
                                                        <button
                                                            onClick={() => handleAction(rider.id, 'reject')}
                                                            className="p-2 bg-red-50 text-red-500 rounded-lg hover:bg-red-100"
                                                            title="Reject"
                                                        >
                                                            <FaTimesCircle />
                                                        </button>
                                                    </>
                                                )}

                                                {rider.status === 'APPROVED' && (
                                                    <button
                                                        onClick={() => handleAction(rider.id, 'suspend')}
                                                        className="p-2 bg-red-50 text-red-500 rounded-lg hover:bg-red-100"
                                                        title="Suspend"
                                                    >
                                                        <FaBan />
                                                    </button>
                                                )}
                                                {rider.status === 'SUSPENDED' && (
                                                    <button
                                                        onClick={() => handleAction(rider.id, 'approve')}
                                                        className="p-2 bg-green-50 text-green-500 rounded-lg hover:bg-green-100"
                                                        title="Re-activate"
                                                    >
                                                        <FaCheckCircle />
                                                    </button>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="5" className="p-8 text-center text-gray-400">
                                        No riders found.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {selectedRiderId && (
                <RiderDetails
                    riderId={selectedRiderId}
                    onClose={() => setSelectedRiderId(null)}
                />
            )}

            {/* Add Rider Modal */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
                        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-center">
                            <h2 className="text-2xl font-bold text-gray-800 flex items-center">
                                <FaMotorcycle className="mr-3 text-red-500" />
                                Add New Rider
                            </h2>
                            <button
                                onClick={() => {
                                    setShowAddModal(false);
                                    resetForm();
                                }}
                                className="p-2 hover:bg-gray-100 rounded-lg transition"
                            >
                                <FaTimes className="text-gray-500" />
                            </button>
                        </div>

                        <form onSubmit={handleAddRider} className="p-6 space-y-6">
                            {/* Personal Information */}
                            <div>
                                <h3 className="text-lg font-bold text-gray-700 mb-4">Personal Information</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">Name *</label>
                                        <input
                                            type="text"
                                            name="name"
                                            value={formData.name}
                                            onChange={handleInputChange}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">Phone * (10 digits)</label>
                                        <input
                                            type="text"
                                            name="phone"
                                            value={formData.phone}
                                            onChange={handleInputChange}
                                            maxLength="10"
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">Email (Login)</label>
                                        <input
                                            type="email"
                                            name="email"
                                            value={formData.email}
                                            onChange={handleInputChange}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">Password *</label>
                                        <input
                                            type="text"
                                            name="password"
                                            value={formData.password}
                                            onChange={handleInputChange}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                            required
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Vehicle Information */}
                            <div>
                                <h3 className="text-lg font-bold text-gray-700 mb-4">Vehicle Information</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">Vehicle Number</label>
                                        <input
                                            type="text"
                                            name="vehicle_number"
                                            value={formData.vehicle_number}
                                            onChange={handleInputChange}
                                            placeholder="GJ-XX-X-XXXX"
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">License Number</label>
                                        <input
                                            type="text"
                                            name="license_number"
                                            value={formData.license_number}
                                            onChange={handleInputChange}
                                            placeholder="GJXXXXXXXXXX"
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Bank Details */}
                            <div>
                                <h3 className="text-lg font-bold text-gray-700 mb-4">Bank Details</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">Account Holder Name</label>
                                        <input
                                            type="text"
                                            name="account_holder_name"
                                            value={formData.account_holder_name}
                                            onChange={handleInputChange}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">Account Number</label>
                                        <input
                                            type="text"
                                            name="account_number"
                                            value={formData.account_number}
                                            onChange={handleInputChange}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">IFSC Code</label>
                                        <input
                                            type="text"
                                            name="ifsc_code"
                                            value={formData.ifsc_code}
                                            onChange={handleInputChange}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">Bank Name</label>
                                        <input
                                            type="text"
                                            name="bank_name"
                                            value={formData.bank_name}
                                            onChange={handleInputChange}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Assignment */}
                            <div>
                                <h3 className="text-lg font-bold text-gray-700 mb-4">Assignment</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">City *</label>
                                        <select
                                            name="city"
                                            value={formData.city}
                                            onChange={handleInputChange}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                            required
                                        >
                                            <option value="Mehsana">Mehsana</option>
                                            <option value="Himmatnagar">Himmatnagar</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                                        <select
                                            name="status"
                                            value={formData.status}
                                            onChange={handleInputChange}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                                        >
                                            <option value="APPROVED">Approved</option>
                                            <option value="PENDING">Pending</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            {/* Submit Button */}
                            <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-3 sm:space-x-3 pt-4 border-t border-gray-200">
                                <button
                                    type="button"
                                    onClick={() => {
                                        setShowAddModal(false);
                                        resetForm();
                                    }}
                                    className="w-full sm:w-auto px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium text-center"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={submitting}
                                    className={`w-full sm:w-auto px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition font-bold text-center ${submitting ? 'opacity-50 cursor-not-allowed' : ''
                                        }`}
                                >
                                    {submitting ? 'Creating...' : 'Create Rider'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RiderManagement;
