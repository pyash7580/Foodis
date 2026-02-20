import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../config';
import toast from 'react-hot-toast';
import { FaSave, FaCog, FaMoneyBillWave, FaPhone, FaLink } from 'react-icons/fa';

const SystemSettings = () => {
    const [settings, setSettings] = useState({});
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [activeTab, setActiveTab] = useState('site_info');

    const TABS = [
        { id: 'site_info', label: 'General', icon: <FaCog /> },
        { id: 'finance', label: 'Finance', icon: <FaMoneyBillWave /> },
        { id: 'contact', label: 'Contact', icon: <FaPhone /> },
        { id: 'app_links', label: 'App Links', icon: <FaLink /> },
    ];

    useEffect(() => {
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token_admin');
            const res = await axios.get(`${API_BASE_URL}/api/admin/settings/`, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' }
            });

            // Transform array to object: { key: { value: JSON.parse(value), id: id } }
            const settingsMap = {};
            res.data.results.forEach(item => {
                try {
                    settingsMap[item.key] = {
                        ...item,
                        parsedValue: JSON.parse(item.value)
                    };
                } catch (e) {
                    console.error(`Failed to parse setting ${item.key}`, e);
                    // Fallback to raw string if not JSON
                    settingsMap[item.key] = { ...item, parsedValue: item.value };
                }
            });
            setSettings(settingsMap);
        } catch (error) {
            console.error("Failed to load settings", error);
            toast.error("Failed to load settings");
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (section, field, value) => {
        setSettings(prev => ({
            ...prev,
            [section]: {
                ...prev[section],
                parsedValue: {
                    ...prev[section]?.parsedValue,
                    [field]: value
                }
            }
        }));
    };

    const handleSave = async (key) => {
        setSubmitting(true);
        try {
            const token = localStorage.getItem('token_admin');
            const setting = settings[key];

            // If ID exists, update. If not, create (though keys are unique)
            // Using PUT/PATCH on the detail endpoint if ID known, or just by key if ViewSet supports lookup_field 'key'

            const payload = {
                key: key,
                value: JSON.stringify(setting.parsedValue),
                description: setting.description
            };

            let url = `${API_BASE_URL}/api/admin/settings/`;
            let method = 'post';

            if (setting.id) {
                // If ID exists, standard update. 
                // But wait, ViewSet lookup_field is 'key'. So url should be /api/admin/settings/{key}/
                url = `${API_BASE_URL}/api/admin/settings/${key}/`;
                method = 'put';
            }

            await axios[method](url, payload, {
                headers: { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' }
            });

            toast.success("Settings saved successfully");
            fetchSettings(); // Refresh to ensure sync
        } catch (error) {
            console.error("Save failed", error);
            toast.error("Failed to save settings");
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-500 font-bold">Loading Settings...</div>;

    const renderField = (section, key, label, type = 'text') => {
        const value = settings[section]?.parsedValue?.[key] || '';
        return (
            <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">{label}</label>
                {type === 'textarea' ? (
                    <textarea
                        value={value}
                        onChange={(e) => handleInputChange(section, key, e.target.value)}
                        className="w-full p-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                        rows="3"
                    />
                ) : type === 'boolean' ? (
                    <div className="flex items-center">
                        <input
                            type="checkbox"
                            checked={!!value}
                            onChange={(e) => handleInputChange(section, key, e.target.checked)}
                            className="w-5 h-5 text-red-600 rounded focus:ring-red-500 border-gray-300"
                        />
                        <span className="ml-2 text-gray-600 text-sm">{value ? 'Enabled' : 'Disabled'}</span>
                    </div>

                ) : (
                    <input
                        type={type}
                        value={value}
                        onChange={(e) => handleInputChange(section, key, e.target.value)}
                        className="w-full p-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                    />
                )}
            </div>
        );
    };

    return (
        <div className="flex flex-col md:flex-row gap-6 h-full">
            {/* Sidebar Tabs */}
            <div className="w-full md:w-64 bg-white rounded-xl shadow-sm border border-gray-100 p-4 h-fit">
                <h3 className="text-lg font-bold text-gray-800 mb-4 px-2">Settings</h3>
                <nav className="space-y-1">
                    {TABS.map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`w-full flex items-center px-4 py-3 rounded-lg transition-colors ${activeTab === tab.id
                                    ? 'bg-red-50 text-red-600 font-bold'
                                    : 'text-gray-600 hover:bg-gray-50'
                                }`}
                        >
                            <span className="mr-3">{tab.icon}</span>
                            {tab.label}
                        </button>
                    ))}
                </nav>
            </div>

            {/* Content Area */}
            <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <div className="flex justify-between items-center mb-6 pb-4 border-b border-gray-100">
                    <h2 className="text-xl font-bold text-gray-800">
                        {TABS.find(t => t.id === activeTab)?.label} Settings
                    </h2>
                    <button
                        onClick={() => handleSave(activeTab)}
                        disabled={submitting}
                        className={`flex items-center px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition disabled:opacity-50`}
                    >
                        <FaSave className="mr-2" />
                        {submitting ? 'Saving...' : 'Save Changes'}
                    </button>
                </div>

                {activeTab === 'site_info' && (
                    <div className="space-y-4 max-w-2xl">
                        {renderField('site_info', 'name', 'Site Name')}
                        {renderField('site_info', 'description', 'Site Description', 'textarea')}
                        {renderField('site_info', 'maintenance_mode', 'Maintenance Mode', 'boolean')}
                    </div>
                )}

                {activeTab === 'finance' && (
                    <div className="space-y-4 max-w-2xl">
                        <div className="grid grid-cols-2 gap-4">
                            {renderField('finance', 'currency', 'Currency Code (e.g. INR)')}
                            {renderField('finance', 'tax_rate', 'Tax Rate (%)', 'number')}
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            {renderField('finance', 'platform_fee', 'Platform Fee', 'number')}
                            {renderField('finance', 'min_order_amount', 'Minimum Order Amount', 'number')}
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            {renderField('finance', 'delivery_charge_base', 'Base Delivery Charge', 'number')}
                            {renderField('finance', 'delivery_charge_per_km', 'Charge per KM', 'number')}
                        </div>
                    </div>
                )}

                {activeTab === 'contact' && (
                    <div className="space-y-4 max-w-2xl">
                        {renderField('contact', 'email', 'Support Email', 'email')}
                        {renderField('contact', 'phone', 'Support Phone', 'tel')}
                        {renderField('contact', 'address', 'Office Address', 'textarea')}
                    </div>
                )}

                {activeTab === 'app_links' && (
                    <div className="space-y-4 max-w-2xl">
                        {renderField('app_links', 'android', 'Android App URL')}
                        {renderField('app_links', 'ios', 'iOS App URL')}
                        {renderField('app_links', 'facebook', 'Facebook URL')}
                        {renderField('app_links', 'instagram', 'Instagram URL')}
                    </div>
                )}
            </div>
        </div>
    );
};

export default SystemSettings;
