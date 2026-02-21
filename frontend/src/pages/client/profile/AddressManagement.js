import { API_BASE_URL } from '../../../config';

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import toast from 'react-hot-toast';
import { useAuth } from '../../../contexts/AuthContext';

// Fix Leaflet icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const LocationMarker = ({ position, setPosition, onPositionChange }) => {
    useMapEvents({
        click(e) {
            setPosition(e.latlng);
            onPositionChange(e.latlng.lat, e.latlng.lng);
        },
    });

    return position === null ? null : (
        <Marker position={position}></Marker>
    );
};

const MapSearch = ({ setMarkerPosition, onSearchChange }) => {
    const [query, setQuery] = useState('');
    const map = useMap();

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;
        try {
            const res = await axios.get(`https://nominatim.openstreetmap.org/search?format=json&q=${query}`, {
                headers: { 'User-Agent': 'FoodisApp/1.0' }
            });
            if (res.data && res.data.length > 0) {
                const { lat, lon } = res.data[0];
                const newPos = { lat: parseFloat(lat), lng: parseFloat(lon) };
                map.flyTo(newPos, 16);
                setMarkerPosition(newPos);
                onSearchChange(lat, lon);
            } else {
                toast.error("Location not found");
            }
        } catch (error) {
            toast.error("Search failed");
        }
    };

    return (
        <div className="absolute top-4 left-4 right-4 z-[1000]">
            <form onSubmit={handleSearch} className="flex space-x-2">
                <input
                    type="text"
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                    placeholder="Search for your area / street..."
                    className="flex-1 bg-white/90 backdrop-blur px-5 py-3 rounded-xl shadow-lg text-sm font-bold border-none outline-none focus:ring-2 ring-red-500"
                />
                <button type="submit" className="bg-red-600 text-white px-5 py-3 rounded-xl shadow-lg font-black text-sm">
                    🔍
                </button>
            </form>
        </div>
    );
};

const AddressManagement = () => {
    const { token } = useAuth();
    const [addresses, setAddresses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [mapCenter, setMapCenter] = useState({ lat: 28.6139, lng: 77.2090 }); // Default Delhi
    const [markerPosition, setMarkerPosition] = useState(null);

    const [formData, setFormData] = useState({
        label: 'Home',
        address_line1: '',
        address_line2: '',
        landmark: '',
        city: '',
        state: '',
        pincode: '',
        is_default: false
    });

    const LABELS = ['Home', 'Work', 'Other'];

    const reverseGeocode = useCallback(async (lat, lng) => {
        try {
            const res = await axios.get(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`, {
                headers: { 'User-Agent': 'FoodisApp/1.0' }
            });
            if (res.data && res.data.address) {
                const addr = res.data.address;
                setFormData(prev => ({
                    ...prev,
                    address_line1: addr.road || addr.suburb || addr.neighbourhood || '',
                    address_line2: addr.suburb || addr.city_district || '',
                    city: addr.city || addr.town || addr.village || '',
                    state: addr.state || '',
                    pincode: addr.postcode || ''
                }));
                toast.success("Location auto-filled!");
            }
        } catch (error) {
            console.error("Geocoding failed", error);
        }
    }, []);

    const fetchAddresses = useCallback(async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/api/auth/addresses/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
            });
            // Handle paginated response
            if (res.data.results && Array.isArray(res.data.results)) {
                setAddresses(res.data.results);
            } else if (Array.isArray(res.data)) {
                setAddresses(res.data);
            } else {
                setAddresses([]);
            }
            setLoading(false);
        } catch (error) {
            toast.error("Failed to load addresses");
            setLoading(false);
        }
    }, [token]);

    const getCurrentLocation = useCallback(() => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(pos => {
                const { latitude, longitude } = pos.coords;
                setMapCenter({ lat: latitude, lng: longitude });
                if (!markerPosition) setMarkerPosition({ lat: latitude, lng: longitude });
            });
        }
    }, [markerPosition]);

    useEffect(() => {
        if (token) {
            fetchAddresses();
        }
        getCurrentLocation();
    }, [token, fetchAddresses, getCurrentLocation]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!markerPosition) {
            toast.error("Please pin location on map");
            return;
        }

        const payload = {
            ...formData,
            latitude: parseFloat(markerPosition.lat).toFixed(6),
            longitude: parseFloat(markerPosition.lng).toFixed(6)
        };

        const loadingToast = toast.loading("Saving address...");
        try {
            if (editingId) {
                await axios.put(`${API_BASE_URL}/api/auth/addresses/${editingId}/`, payload, {
                    headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
                });
                toast.success("Address updated", { id: loadingToast });
            } else {
                await axios.post(`${API_BASE_URL}/api/auth/addresses/`, payload, {
                    headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
                });
                toast.success("Address added", { id: loadingToast });
            }
            setShowModal(false);
            resetForm();
            fetchAddresses();
        } catch (error) {
            const errorMsg = error.response?.data
                ? Object.entries(error.response.data).map(([k, v]) => `${k}: ${v}`).join(', ')
                : "Failed to save address. Check all fields.";
            toast.error(errorMsg, { id: loadingToast });
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Delete this address?")) return;
        try {
            await axios.delete(`${API_BASE_URL}/api/auth/addresses/${id}/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'CLIENT' }
            });
            toast.success("Address deleted");
            fetchAddresses();
        } catch (error) {
            toast.error("Failed to delete address");
        }
    };

    const handleEdit = (addr) => {
        setEditingId(addr.id);
        setFormData({
            label: addr.label,
            address_line1: addr.address_line1,
            address_line2: addr.address_line2,
            landmark: addr.landmark,
            city: addr.city,
            state: addr.state,
            pincode: addr.pincode,
            is_default: addr.is_default
        });
        setMarkerPosition({ lat: parseFloat(addr.latitude), lng: parseFloat(addr.longitude) });
        setMapCenter({ lat: parseFloat(addr.latitude), lng: parseFloat(addr.longitude) });
        setShowModal(true);
    };

    const resetForm = () => {
        setEditingId(null);
        setFormData({
            label: 'Home',
            address_line1: '',
            address_line2: '',
            landmark: '',
            city: '',
            state: '',
            pincode: '',
            is_default: false
        });
        setMarkerPosition(mapCenter);
    };

    if (loading) return <div className="p-8 text-center text-gray-400 font-bold">Loading Addresses...</div>;

    return (
        <div>
            <header className="flex justify-between items-center mb-8">
                <h1 className="text-2xl font-black text-gray-900">My Addresses</h1>
                <button
                    onClick={() => { resetForm(); setShowModal(true); }}
                    className="bg-red-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-red-700 transition shadow-lg shadow-red-100"
                >
                    + Add New Address
                </button>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {addresses.map(addr => (
                    <div key={addr.id} className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 relative group">
                        <div className="flex justify-between items-start mb-4">
                            <div className="px-3 py-1 bg-gray-100 rounded-lg text-xs font-black uppercase tracking-widest text-gray-600">
                                {addr.label}
                            </div>
                            <div className="flex space-x-2 opacity-0 group-hover:opacity-100 transition">
                                <button onClick={() => handleEdit(addr)} className="text-blue-600 font-bold text-sm">Valid</button>
                                <button onClick={() => handleDelete(addr.id)} className="text-red-500 font-bold text-sm">Delete</button>
                            </div>
                        </div>
                        <p className="text-gray-900 font-bold mb-1">{addr.address_line1}</p>
                        <p className="text-gray-500 text-sm mb-4">{addr.address_line2}, {addr.landmark}, {addr.city} - {addr.pincode}</p>
                        {addr.is_default && (
                            <span className="text-green-600 text-xs font-black uppercase tracking-widest">✅ Default Address</span>
                        )}
                    </div>
                ))}
                {addresses.length === 0 && (
                    <div className="col-span-2 text-center py-12 bg-white rounded-3xl border border-dashed border-gray-200">
                        <p className="text-gray-400 font-bold">No addresses found.</p>
                    </div>
                )}
            </div>

            {/* Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
                    <div className="bg-white w-full max-w-4xl rounded-3xl overflow-hidden shadow-2xl flex flex-col md:flex-row max-h-[90vh]">
                        {/* Map Side */}
                        <div className="w-full md:w-1/2 h-64 md:h-auto bg-gray-100 relative">
                            <MapContainer
                                center={mapCenter}
                                zoom={15}
                                style={{ height: '100%', width: '100%' }}
                            >
                                <TileLayer
                                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                    attribution='&copy; OpenStreetMap contributors'
                                />
                                <MapSearch
                                    setMarkerPosition={setMarkerPosition}
                                    onSearchChange={reverseGeocode}
                                />
                                <LocationMarker
                                    position={markerPosition}
                                    setPosition={setMarkerPosition}
                                    onPositionChange={reverseGeocode}
                                />
                            </MapContainer>
                            <div className="absolute bottom-4 left-4 right-4 bg-white/70 backdrop-blur p-3 rounded-xl text-[10px] font-black uppercase tracking-widest text-center shadow-lg border border-white/50 z-[1000]">
                                Pin location or use search for auto-fill
                            </div>
                        </div>

                        {/* Form Side */}
                        <div className="w-full md:w-1/2 p-8 overflow-y-auto">
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-xl font-black text-gray-900">{editingId ? 'Edit Address' : 'Add Address'}</h2>
                                <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-900 text-xl">✕</button>
                            </div>
                            <form onSubmit={handleSubmit} className="space-y-4">
                                <div>
                                    <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Label</label>
                                    <div className="flex space-x-2">
                                        {LABELS.map(l => (
                                            <button
                                                key={l}
                                                type="button"
                                                onClick={() => setFormData({ ...formData, label: l })}
                                                className={`px-4 py-2 rounded-lg text-xs font-black transition ${formData.label === l ? 'bg-red-600 text-white shadow-md' : 'bg-gray-100 text-gray-500'}`}
                                            >
                                                {l}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                                <div>
                                    <input
                                        required
                                        value={formData.address_line1}
                                        onChange={e => setFormData({ ...formData, address_line1: e.target.value })}
                                        className="w-full bg-gray-50 border-gray-100 rounded-xl p-3 text-sm font-bold outline-none ring-offset-0 focus:ring-2 ring-red-100"
                                        placeholder="Flat / House / Floor / Building *"
                                    />
                                </div>
                                <div>
                                    <input
                                        value={formData.address_line2}
                                        onChange={e => setFormData({ ...formData, address_line2: e.target.value })}
                                        className="w-full bg-gray-50 border-gray-100 rounded-xl p-3 text-sm font-bold outline-none ring-offset-0 focus:ring-2 ring-red-100"
                                        placeholder="Area / Sector / Locality"
                                    />
                                </div>
                                <div>
                                    <input
                                        value={formData.landmark}
                                        onChange={e => setFormData({ ...formData, landmark: e.target.value })}
                                        className="w-full bg-gray-50 border-gray-100 rounded-xl p-3 text-sm font-bold outline-none ring-offset-0 focus:ring-2 ring-red-100"
                                        placeholder="Nearby Landmark (Optional)"
                                    />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <input
                                        required
                                        value={formData.city}
                                        onChange={e => setFormData({ ...formData, city: e.target.value })}
                                        className="w-full bg-gray-50 border-gray-100 rounded-xl p-3 text-sm font-bold outline-none ring-offset-0 focus:ring-2 ring-red-100"
                                        placeholder="City *"
                                    />
                                    <input
                                        required
                                        value={formData.pincode}
                                        onChange={e => setFormData({ ...formData, pincode: e.target.value })}
                                        className="w-full bg-gray-50 border-gray-100 rounded-xl p-3 text-sm font-bold outline-none ring-offset-0 focus:ring-2 ring-red-100"
                                        placeholder="Pincode *"
                                    />
                                </div>
                                <input
                                    required
                                    value={formData.state}
                                    onChange={e => setFormData({ ...formData, state: e.target.value })}
                                    className="w-full bg-gray-50 border-gray-100 rounded-xl p-3 text-sm font-bold outline-none ring-offset-0 focus:ring-2 ring-red-100"
                                    placeholder="State *"
                                />

                                <div className="flex items-center space-x-2 py-2">
                                    <input
                                        type="checkbox"
                                        id="default"
                                        checked={formData.is_default}
                                        onChange={e => setFormData({ ...formData, is_default: e.target.checked })}
                                        className="rounded text-red-600 focus:ring-red-500 border-gray-300"
                                    />
                                    <label htmlFor="default" className="text-sm font-bold text-gray-700">Set as default address</label>
                                </div>

                                <button type="submit" className="w-full py-3 bg-red-600 text-white rounded-xl font-black shadow-lg shadow-red-100 hover:bg-red-700 transition">
                                    {editingId ? 'Update Address' : 'Save Address'}
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AddressManagement;
