import { API_BASE_URL } from '../../config';

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../../contexts/AuthContext';

const MenuManagement = () => {
    const { logout } = useAuth();
    const [menuItems, setMenuItems] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingItem, setEditingItem] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        price: '',
        category: '',
        veg_type: 'VEG',
        is_available: true,
        image: null
    });

    const fetchData = useCallback(async () => {
        try {
            const [menuRes, catRes] = await Promise.all([
                axios.get(`${API_BASE_URL}/api/restaurant/menu-items/`),
                axios.get(`${API_BASE_URL}/api/client/categories/`)
            ]);

            // Handle pagination (results array vs direct array)
            const menuData = menuRes.data.results || menuRes.data;
            const catData = catRes.data.results || catRes.data;

            setMenuItems(Array.isArray(menuData) ? menuData : []);
            setCategories(Array.isArray(catData) ? catData : []);
            setLoading(false);
        } catch (error) {
            console.error("Fetch error", error);
            toast.error("Failed to load menu data");
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleToggleAvailability = async (id) => {
        try {
            await axios.post(`${API_BASE_URL}/api/restaurant/menu-items/${id}/toggle_availability/`);
            toast.success("Availability updated");
            fetchData();
        } catch (error) {
            toast.error("Failed to update status");
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const data = new FormData();
        Object.keys(formData).forEach(key => {
            if (key === 'image' && !formData[key]) return;
            data.append(key, formData[key]);
        });

        try {
            if (editingItem) {
                await axios.patch(`${API_BASE_URL}/api/restaurant/menu-items/${editingItem.id}/`, data);
                toast.success("Item updated");
            } else {
                await axios.post(`${API_BASE_URL}/api/restaurant/menu-items/`, data);
                toast.success("Item added to menu");
            }
            setShowModal(false);
            setEditingItem(null);
            setFormData({
                name: '', description: '', price: '', category: '', veg_type: 'VEG', is_available: true, image: null
            });
            fetchData();
        } catch (error) {
            toast.error("Failed to save menu item");
        }
    };

    const handleEdit = (item) => {
        setEditingItem(item);
        setFormData({
            name: item.name,
            description: item.description,
            price: item.price,
            category: item.category,
            veg_type: item.veg_type,
            is_available: item.is_available,
            image: null
        });
        setShowModal(true);
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Are you sure you want to delete this item?")) return;
        try {
            await axios.delete(`${API_BASE_URL}/api/restaurant/menu-items/${id}/`);
            toast.success("Item deleted");
            fetchData();
        } catch (error) {
            toast.error("Failed to delete item");
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-500 font-bold">Loading Menu...</div>;

    return (
        <div className="min-h-screen bg-[#fcfcfc] flex">
            {/* Reuse Sidebar component logic or just simple links here for consistency */}
            <aside className="w-64 bg-white border-r border-gray-100 hidden lg:flex flex-col sticky top-0 h-screen">
                <div className="p-6 border-b border-gray-50">
                    <h2 className="text-2xl font-black text-red-600 tracking-tighter">FOODIS<span className="text-gray-900">.Biz</span></h2>
                </div>
                <nav className="flex-grow p-4 space-y-2">
                    <Link to="/restaurant/dashboard" className="flex items-center space-x-3 p-3 text-gray-500 hover:bg-gray-50 rounded-xl font-medium transition">
                        <span>📊</span> <span>Dashboard</span>
                    </Link>
                    <Link to="/restaurant/menu" className="flex items-center space-x-3 p-3 bg-red-50 text-red-600 rounded-xl font-bold">
                        <span>🍔</span> <span>Menu Management</span>
                    </Link>
                    <Link to="/restaurant/earnings" className="flex items-center space-x-3 p-3 text-gray-500 hover:bg-gray-50 rounded-xl font-medium transition">
                        <span>💰</span> <span>Earnings & Reports</span>
                    </Link>
                    <Link to="/restaurant/profile" className="flex items-center space-x-3 p-3 text-gray-500 hover:bg-gray-50 rounded-xl font-medium transition">
                        <span>🏢</span> <span>Restaurant Profile</span>
                    </Link>
                </nav>
                <div className="p-4 border-t border-gray-50">
                    <button onClick={logout} className="flex items-center space-x-3 p-3 w-full text-red-400 hover:bg-red-50 rounded-xl font-medium transition">
                        <span>🚪</span> <span>Logout</span>
                    </button>
                </div>
            </aside>

            <main className="flex-grow w-full min-w-0 p-4 md:p-8 pb-28 md:pb-8">
                <header className="flex flex-col md:flex-row md:justify-between items-start md:items-center gap-4 mb-10">
                    <div>
                        <h1 className="text-3xl font-black text-gray-900">Menu Management</h1>
                        <p className="text-gray-500 mt-1">Add, edit and manage your dishes.</p>
                    </div>
                    <button
                        onClick={() => { setEditingItem(null); setShowModal(true); }}
                        className="bg-red-600 text-white px-6 py-3 rounded-2xl font-bold flex items-center space-x-2 shadow-lg shadow-red-100"
                    >
                        <span>➕</span> <span>Add New Item</span>
                    </button>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {menuItems.map(item => (
                        <div key={item.id} className={`bg-white rounded-3xl overflow-hidden shadow-sm border border-gray-50 flex flex-col ${!item.is_available ? 'opacity-60 grayscale-[0.5]' : ''}`}>
                            <div className="h-48 bg-gray-100 relative overflow-hidden group">
                                {item.image ? (
                                    <img
                                        src={item.image.startsWith('http') ? item.image : (item.image.startsWith('/') ? `${API_BASE_URL}${item.image}` : `${API_BASE_URL}/${item.image}`)}
                                        alt={item.name}
                                        className="w-full h-full object-cover group-hover:scale-105 transition duration-500"
                                    />
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center text-4xl">🍲</div>
                                )}
                                <div className="absolute top-4 left-4 bg-white/90 backdrop-blur rounded-lg px-3 py-1 text-[10px] font-black uppercase tracking-widest text-gray-800 shadow-sm">
                                    {categories.find(c => c.id === item.category)?.name || 'Dish'}
                                </div>
                            </div>

                            <div className="p-6 flex-grow">
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="text-lg font-black text-gray-900 leading-tight">{item.name}</h3>
                                    <span className="font-black text-red-600">₹{item.price}</span>
                                </div>
                                <p className="text-gray-400 text-sm line-clamp-2 mb-6 font-medium leading-relaxed">
                                    {item.description || "Fresh and delicious, prepared with the finest ingredients."}
                                </p>

                                <div className="flex items-center justify-between mt-auto pt-4 border-t border-gray-50">
                                    <div className="flex items-center space-x-2">
                                        <div className={`w-3 h-3 rounded-full ${item.veg_type === 'VEG' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                                        <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">{item.veg_type}</span>
                                    </div>
                                    <div className="flex space-x-2">
                                        <button onClick={() => handleToggleAvailability(item.id)} className={`p-2 rounded-xl transition ${item.is_available ? 'bg-green-50 text-green-600' : 'bg-gray-100 text-gray-400'}`}>
                                            {item.is_available ? '🟢' : '⚪'}
                                        </button>
                                        <button onClick={() => handleEdit(item)} className="p-2 bg-blue-50 text-blue-600 rounded-xl hover:bg-blue-100 transition">
                                            ✏️
                                        </button>
                                        <button onClick={() => handleDelete(item.id)} className="p-2 bg-red-50 text-red-600 rounded-xl hover:bg-red-100 transition">
                                            🗑️
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Modal */}
                {showModal && (
                    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                        <div className="bg-white w-full max-w-xl rounded-3xl overflow-hidden shadow-2xl animate-in zoom-in-95 duration-200">
                            <div className="p-8 border-b border-gray-50 flex justify-between items-center bg-gray-50/50">
                                <h2 className="text-2xl font-black text-gray-900">{editingItem ? 'Edit Dish' : 'Add New Dish'}</h2>
                                <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-900 text-2xl">✕</button>
                            </div>
                            <form onSubmit={handleSubmit} className="p-8 space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="col-span-1 md:col-span-2">
                                        <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Dish Name</label>
                                        <input
                                            required
                                            value={formData.name}
                                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                            className="w-full bg-gray-50 border border-gray-100 rounded-2xl p-4 font-bold text-gray-900 focus:ring-4 focus:ring-red-100 focus:border-red-500 transition outline-none"
                                            placeholder="e.g. Paneer Butter Masala"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Price (₹)</label>
                                        <input
                                            required
                                            type="number"
                                            value={formData.price}
                                            onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                                            className="w-full bg-gray-50 border border-gray-100 rounded-2xl p-4 font-bold text-gray-900 focus:ring-4 focus:ring-red-100 focus:border-red-500 transition outline-none"
                                            placeholder="250"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Category</label>
                                        <select
                                            required
                                            value={formData.category}
                                            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                                            className="w-full bg-gray-50 border border-gray-100 rounded-2xl p-4 font-bold text-gray-900 focus:ring-4 focus:ring-red-100 focus:border-red-500 transition outline-none appearance-none"
                                        >
                                            <option value="">Select Category</option>
                                            {categories.map(cat => (
                                                <option key={cat.id} value={cat.id}>{cat.name}</option>
                                            ))}
                                        </select>
                                    </div>
                                    <div className="col-span-1 md:col-span-2">
                                        <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Description</label>
                                        <textarea
                                            rows="2"
                                            value={formData.description}
                                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                            className="w-full bg-gray-50 border border-gray-100 rounded-2xl p-4 font-bold text-gray-900 focus:ring-4 focus:ring-red-100 focus:border-red-500 transition outline-none"
                                            placeholder="Detailed description of the dish..."
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Veg/Non-Veg</label>
                                        <div className="flex bg-gray-100 p-1 rounded-xl">
                                            {['VEG', 'NON-VEG'].map(type => (
                                                <button
                                                    key={type}
                                                    type="button"
                                                    onClick={() => setFormData({ ...formData, veg_type: type })}
                                                    className={`flex-1 py-2 text-[10px] font-black rounded-lg transition ${formData.veg_type === type ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-400'}`}
                                                >
                                                    {type}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                    <div>
                                        <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Dish Image</label>
                                        <input
                                            type="file"
                                            onChange={(e) => setFormData({ ...formData, image: e.target.files[0] })}
                                            className="w-full text-xs font-bold text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-black file:bg-red-50 file:text-red-700 hover:file:bg-red-100"
                                        />
                                    </div>
                                </div>
                                <button type="submit" className="w-full py-4 bg-red-600 text-white rounded-2xl font-black text-lg shadow-xl shadow-red-100 hover:bg-red-700 transition transform hover:scale-[1.01]">
                                    {editingItem ? 'Save Changes' : 'Create Dish'}
                                </button>
                            </form>
                        </div>
                    </div>
                )}
            </main>

            {/* Mobile Bottom Navigation */}
            <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 flex justify-around items-center p-3 z-50 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] pb-6 md:pb-3">
                <Link to="/restaurant/dashboard" className={`flex flex-col items-center p-2 rounded-xl text-gray-400`}>
                    <span className="text-xl mb-1">📊</span>
                    <span className="text-[10px] font-bold">Dashboard</span>
                </Link>
                <Link to="/restaurant/menu" className={`flex flex-col items-center p-2 rounded-xl text-red-600`}>
                    <span className="text-xl mb-1">🍔</span>
                    <span className="text-[10px] font-bold">Menu</span>
                </Link>
                <Link to="/restaurant/earnings" className={`flex flex-col items-center p-2 rounded-xl text-gray-400`}>
                    <span className="text-xl mb-1">💰</span>
                    <span className="text-[10px] font-bold">Earnings</span>
                </Link>
                <Link to="/restaurant/profile" className={`flex flex-col items-center p-2 rounded-xl text-gray-400`}>
                    <span className="text-xl mb-1">🏢</span>
                    <span className="text-[10px] font-bold">Profile</span>
                </Link>
            </div>
        </div>
    );
};

export default MenuManagement;
