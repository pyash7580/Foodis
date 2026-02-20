
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../config';
import toast from 'react-hot-toast';
import { FaSearch, FaFilter, FaShoppingBag, FaEye, FaCheckCircle, FaTimesCircle, FaBan, FaTruck, FaClock } from 'react-icons/fa';
import AdminOrderDetails from './AdminOrderDetails';
import { format } from 'date-fns';

const OrderManagement = () => {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('ALL');
    const [selectedOrderId, setSelectedOrderId] = useState(null);

    useEffect(() => {
        fetchOrders();
    }, []);

    const fetchOrders = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token_admin');
            const res = await axios.get(`${API_BASE_URL}/api/admin/orders/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' }
            });
            const data = res.data.results ? res.data.results : res.data;
            if (Array.isArray(data)) {
                setOrders(data);
            }
        } catch (error) {
            console.error("Failed to fetch orders", error);
            toast.error("Failed to load orders");
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'DELIVERED': return 'bg-green-100 text-green-700';
            case 'CANCELLED': return 'bg-red-100 text-red-700';
            case 'PENDING': return 'bg-yellow-100 text-yellow-700';
            default: return 'bg-blue-100 text-blue-700';
        }
    };

    const filteredOrders = orders.filter(order => {
        const matchesSearch =
            order.order_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
            order.user_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            order.restaurant_name.toLowerCase().includes(searchTerm.toLowerCase());

        const matchesStatus = filterStatus === 'ALL' ? true : order.status === filterStatus;
        return matchesSearch && matchesStatus;
    });

    if (loading) return <div className="p-8 text-center text-gray-500 font-bold">Loading Orders...</div>;

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-gray-800 flex items-center">
                <FaShoppingBag className="mr-3 text-red-500" />
                Order Monitoring
            </h1>

            {/* Header & Controls */}
            <div className="flex flex-col md:flex-row justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-gray-100 gap-4">
                <div className="relative w-full md:w-96">
                    <FaSearch className="absolute top-3.5 left-4 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search ID, Customer, Restaurant..."
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
                        <option value="PENDING">Pending</option>
                        <option value="CONFIRMED">Confirmed</option>
                        <option value="PREPARING">Preparing</option>
                        <option value="PICKED_UP">Picked Up</option>
                        <option value="DELIVERED">Delivered</option>
                        <option value="CANCELLED">Cancelled</option>
                    </select>
                </div>
            </div>

            {/* Orders Table */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm text-gray-600">
                        <thead className="bg-gray-50 text-gray-800 uppercase tracking-wider font-bold">
                            <tr>
                                <th className="p-4">Order ID & Date</th>
                                <th className="p-4">Customer</th>
                                <th className="p-4">Restaurant</th>
                                <th className="p-4 text-right">Amount</th>
                                <th className="p-4 text-center">Status</th>
                                <th className="p-4 text-center">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {filteredOrders.length > 0 ? (
                                filteredOrders.map(order => (
                                    <tr key={order.id} className="hover:bg-gray-50 transition">
                                        <td className="p-4">
                                            <div className="font-bold text-gray-800">#{order.order_id}</div>
                                            <div className="text-xs text-gray-400">
                                                {format(new Date(order.placed_at), 'MMM dd, yyyy HH:mm')}
                                            </div>
                                        </td>
                                        <td className="p-4">
                                            <div className="font-medium text-gray-800">{order.user_name}</div>
                                        </td>
                                        <td className="p-4">
                                            <div className="font-medium text-gray-800">{order.restaurant_name}</div>
                                        </td>
                                        <td className="p-4 text-right">
                                            <div className="font-bold text-gray-900">₹{parseFloat(order.total).toLocaleString()}</div>
                                            <span className="text-[10px] text-gray-400 uppercase">{order.payment_method}</span>
                                        </td>
                                        <td className="p-4 text-center">
                                            <span className={`px-3 py-1 rounded-full text-xs font-bold ${getStatusColor(order.status)}`}>
                                                {order.status}
                                            </span>
                                        </td>
                                        <td className="p-4 text-center">
                                            <button
                                                onClick={() => setSelectedOrderId(order.id)}
                                                className="flex items-center space-x-2 p-2 bg-blue-50 text-blue-500 rounded-lg hover:bg-blue-100 transition whitespace-nowrap"
                                                title="View Order"
                                            >
                                                <FaEye />
                                                <span className="text-xs font-bold">View Order</span>
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="6" className="p-8 text-center text-gray-400">
                                        No orders found.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {selectedOrderId && (
                <AdminOrderDetails
                    orderId={selectedOrderId}
                    onClose={() => setSelectedOrderId(null)}
                />
            )}
        </div>
    );
};

export default OrderManagement;
