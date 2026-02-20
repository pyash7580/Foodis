
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../config';
import toast from 'react-hot-toast';
import { FaSearch, FaBan, FaCheckCircle, FaEye, FaMapMarkerAlt, FaFilter } from 'react-icons/fa';
import { format } from 'date-fns';
import UserDetails from './UserDetails';

const UserManagement = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterRole, setFilterRole] = useState('CLIENT'); // CLIENT, RESTAURANT, RIDER, ADMIN, ALL
    const [filterStatus, setFilterStatus] = useState('ALL'); // ALL, ACTIVE, BLOCKED
    const [selectedUserId, setSelectedUserId] = useState(null);
    const [errorMsg, setErrorMsg] = useState(null);

    useEffect(() => {
        fetchUsers();
    }, [filterRole]);

    const fetchUsers = async () => {
        setLoading(true);
        setErrorMsg(null);
        try {
            const token = localStorage.getItem('token_admin');
            let url = `${API_BASE_URL}/api/admin/users/`;
            if (filterRole !== 'ALL') {
                url += `?role=${filterRole}`;
            }
            const res = await axios.get(url, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' }
            });
            const data = res.data.results ? res.data.results : res.data;

            if (Array.isArray(data)) {
                setUsers(data);
            } else {

                console.error("API response is not an array:", data);
                toast.error("Invalid data received");
            }
        } catch (error) {
            console.error("Failed to fetch users", error);
            setErrorMsg("Failed to load users. " + (error.message || ""));
            toast.error("Failed to load users");
        } finally {
            setLoading(false);
        }
    };

    const handleBlockUnblock = async (userId, currentStatus) => {
        const action = currentStatus ? 'block_user' : 'unblock_user';
        const confirmMsg = currentStatus
            ? "Are you sure you want to BLOCK this user? They will not be able to order."
            : "Are you sure you want to UNBLOCK this user?";

        if (!window.confirm(confirmMsg)) return;

        try {
            const token = localStorage.getItem('token_admin');
            await axios.post(`${API_BASE_URL}/api/admin/users/${userId}/${action}/`, {}, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' }
            });
            toast.success(`User ${currentStatus ? 'Blocked' : 'Activated'} Successfully`);
            fetchUsers(); // Refresh list
        } catch (error) {
            console.error("Action failed", error);
            toast.error("Failed to update user status");
        }
    };

    // Filtering logic
    const filteredUsers = users.filter(user => {
        const matchesSearch =
            (user.name?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
            (user.phone?.includes(searchTerm)) ||
            (user.email?.toLowerCase() || '').includes(searchTerm.toLowerCase());

        const matchesStatus =
            filterStatus === 'ALL' ? true :
                filterStatus === 'ACTIVE' ? user.is_active :
                    !user.is_active;

        return matchesSearch && matchesStatus;
    });

    if (loading) return <div className="p-8 text-center text-gray-500 font-bold">Loading Users...</div>;

    return (
        <div className="space-y-6">
            {errorMsg && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                    <strong className="font-bold">Debug Error: </strong>
                    <span className="block sm:inline">{errorMsg}</span>
                    <br />
                    <small>API: {API_BASE_URL}/api/admin/users/</small>
                </div>
            )}

            {/* Header & Controls */}
            <div className="flex flex-col md:flex-row justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-gray-100 gap-4">
                <div className="relative w-full md:w-96">
                    <FaSearch className="absolute top-3.5 left-4 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search by Name, Mobile, Email..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-12 pr-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-red-500"
                    />
                </div>

                <div className="flex flex-wrap items-center gap-4">
                    <div className="flex items-center space-x-2">
                        <span className="text-gray-400 text-sm font-bold">Role:</span>
                        <select
                            value={filterRole}
                            onChange={(e) => setFilterRole(e.target.value)}
                            className="p-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 bg-white"
                        >
                            <option value="CLIENT">Clients</option>
                            <option value="ADMIN">Admins</option>
                            <option value="RESTAURANT">Restaurants</option>
                            <option value="RIDER">Riders</option>
                            <option value="ALL">All Users</option>
                        </select>
                    </div>

                    <div className="flex items-center space-x-2">
                        <span className="text-gray-400 text-sm font-bold">Status:</span>
                        <select
                            value={filterStatus}
                            onChange={(e) => setFilterStatus(e.target.value)}
                            className="p-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 bg-white"
                        >
                            <option value="ALL">All Status</option>
                            <option value="ACTIVE">Active</option>
                            <option value="BLOCKED">Blocked</option>
                        </select>
                    </div>
                </div>

            </div>

            {/* Users Table */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm text-gray-600">
                        <thead className="bg-gray-50 text-gray-800 uppercase tracking-wider font-bold">
                            <tr>
                                <th className="p-4">User</th>
                                <th className="p-4">Contact</th>
                                <th className="p-4">Location</th>
                                <th className="p-4 text-center">Orders</th>
                                <th className="p-4 text-center">Spent</th>
                                <th className="p-4 text-center">Status</th>
                                <th className="p-4 text-center">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {filteredUsers.length > 0 ? (
                                filteredUsers.map(user => (
                                    <tr key={user.id} className="hover:bg-gray-50 transition">
                                        <td className="p-4">
                                            <p className="font-bold text-gray-800">{user.name || 'Unhamed User'}</p>
                                            <p className="text-xs text-gray-400">ID: #{user.id}</p>
                                        </td>
                                        <td className="p-4">
                                            <p>{user.phone || 'N/A'}</p>
                                            <p className="text-xs text-gray-400">{user.email}</p>
                                        </td>
                                        <td className="p-4">
                                            <div className="flex items-center">
                                                <FaMapMarkerAlt className="text-gray-300 mr-1" />
                                                {user.city || 'N/A'}
                                            </div>
                                        </td>
                                        <td className="p-4 text-center font-medium">
                                            {user.total_orders}
                                        </td>
                                        <td className="p-4 text-center font-bold text-green-600">
                                            ₹{user.total_spent?.toLocaleString()}
                                        </td>
                                        <td className="p-4 text-center">
                                            <span className={`px-3 py-1 rounded-full text-xs font-bold ${user.is_active
                                                ? 'bg-green-100 text-green-700'
                                                : 'bg-red-100 text-red-700'
                                                }`}>
                                                {user.is_active ? 'Active' : 'Blocked'}
                                            </span>
                                        </td>
                                        <td className="p-4 text-center">
                                            <div className="flex items-center justify-center space-x-2">
                                                <button
                                                    onClick={() => handleBlockUnblock(user.id, user.is_active)}
                                                    className={`p-2 rounded-lg transition ${user.is_active
                                                        ? 'bg-red-50 text-red-500 hover:bg-red-100'
                                                        : 'bg-green-50 text-green-500 hover:bg-green-100'
                                                        }`}
                                                    title={user.is_active ? "Block User" : "Unblock User"}
                                                >
                                                    {user.is_active ? <FaBan /> : <FaCheckCircle />}
                                                </button>
                                                {/* Details button placeholder */}
                                                <button
                                                    onClick={() => setSelectedUserId(user.id)}
                                                    className="p-2 bg-gray-50 text-gray-500 rounded-lg hover:bg-gray-100"
                                                    title="View Profile"
                                                >
                                                    <FaEye />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="7" className="p-8 text-center text-gray-400">
                                        No users found matching your search.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {selectedUserId && (
                <UserDetails
                    userId={selectedUserId}
                    onClose={() => setSelectedUserId(null)}
                />
            )}
        </div>
    );
};

export default UserManagement;
