import { API_BASE_URL } from '../../../config';

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Navbar from '../../../components/Navbar';
import { useAuth } from '../../../contexts/AuthContext';
import { toast } from 'react-hot-toast';

const RestaurantOnboarding = () => {
    const { token } = useAuth();
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);

    // Form Data
    const [formData, setFormData] = useState({
        name: '',
        cuisine: '',
        phone: '',
        email: '',
        address: '',
        city: '',
        state: '',
        pincode: '',
        gst_number: '',
        pan_number: '',
        fssai_license: '',
        bank_account_number: '',
        ifsc_code: '',
        bank_name: ''
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const config = {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'X-Role': 'RESTAURANT'
                }
            };

            // 1. Create Restaurant Basic Info
            const restaurantRes = await axios.post(`${API_BASE_URL}/api/restaurant/restaurant/`, {
                name: formData.name,
                cuisine: formData.cuisine,
                phone: formData.phone,
                email: formData.email,
                address: formData.address,
                city: formData.city,
                state: formData.state,
                pincode: formData.pincode,
                latitude: 12.9716, // Default or add geolocation later
                longitude: 77.5946,
                slug: formData.name.toLowerCase().replace(/ /g, '-') + '-' + Date.now().toString().slice(-4)
            }, config);

            // 2. Update Profile with Banking & Docs
            await axios.put(`${API_BASE_URL}/api/restaurant/restaurant/${restaurantRes.data.id}/profile/`, {
                gst_number: formData.gst_number,
                pan_number: formData.pan_number,
                fssai_license: formData.fssai_license,
                bank_account_number: formData.bank_account_number,
                ifsc_code: formData.ifsc_code,
                bank_name: formData.bank_name
            }, config);

            toast.success("Application submitted successfully!");
            navigate('/restaurant/pending');

        } catch (error) {
            console.error(error);
            let errMsg = "Failed to submit application. Please verify all fields.";
            if (error.response && error.response.data) {
                if (typeof error.response.data === 'object') {
                    const fields = Object.keys(error.response.data);
                    const messages = Object.values(error.response.data).flat();
                    errMsg = `${fields[0].toUpperCase()}: ${messages[0]}`;
                } else if (typeof error.response.data === 'string') {
                    errMsg = error.response.data;
                }
            }
            toast.error(errMsg);
        } finally {
            setLoading(false);
        }
    };

    const nextStep = () => setStep(step + 1);
    const prevStep = () => setStep(step - 1);

    return (
        <div className="min-h-screen bg-gray-50 pb-12">
            <Navbar />

            <div className="max-w-3xl mx-auto pt-10 px-4">
                {/* Progress Bar */}
                <div className="mb-8">
                    <div className="flex items-center justify-between text-xs font-bold uppercase tracking-widest text-gray-500 mb-2">
                        <span className={step >= 1 ? 'text-red-600' : ''}>Basics</span>
                        <span className={step >= 2 ? 'text-red-600' : ''}>Address</span>
                        <span className={step >= 3 ? 'text-red-600' : ''}>Legal</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-red-600 transition-all duration-500 ease-out"
                            style={{ width: `${(step / 3) * 100}%` }}
                        ></div>
                    </div>
                </div>

                <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
                    <div className="bg-red-600 p-6 text-white text-center">
                        <h1 className="text-2xl font-black">Complete your Registration</h1>
                        <p className="opacity-90 mt-1 text-sm">Step {step} of 3</p>
                    </div>

                    <form onSubmit={handleSubmit} className="p-8">
                        {step === 1 && (
                            <div className="space-y-6 animate-in slide-in-from-right-8 fade-in">
                                <h2 className="text-xl font-bold text-gray-900">Restaurant Information</h2>
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-1">Restaurant Name</label>
                                    <input required name="name" value={formData.name} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg font-bold outline-none focus:ring-2 focus:ring-red-500" placeholder="e.g. Spice Garden" />
                                </div>
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-1">Cuisine Type</label>
                                    <input required name="cuisine" value={formData.cuisine} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg font-bold outline-none focus:ring-2 focus:ring-red-500" placeholder="e.g. North Indian, Chinese" />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-bold text-gray-700 mb-1">Contact Phone</label>
                                        <input required name="phone" value={formData.phone} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg font-bold outline-none focus:ring-2 focus:ring-red-500" />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-bold text-gray-700 mb-1">Email Address</label>
                                        <input required type="email" name="email" value={formData.email} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg font-bold outline-none focus:ring-2 focus:ring-red-500" />
                                    </div>
                                </div>
                                <div className="pt-6 flex justify-end">
                                    <button type="button" onClick={nextStep} className="px-8 py-3 bg-red-600 text-white font-bold rounded-xl hover:bg-red-700 transition">
                                        Next : Address
                                    </button>
                                </div>
                            </div>
                        )}

                        {step === 2 && (
                            <div className="space-y-6 animate-in slide-in-from-right-8 fade-in">
                                <h2 className="text-xl font-bold text-gray-900">Location Details</h2>
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-1">Full Address</label>
                                    <textarea required name="address" rows="3" value={formData.address} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg font-bold outline-none focus:ring-2 focus:ring-red-500" placeholder="Shop No, Street, Landmark" />
                                </div>
                                <div className="grid grid-cols-3 gap-4">
                                    <div>
                                        <label className="block text-sm font-bold text-gray-700 mb-1">City</label>
                                        <input required name="city" value={formData.city} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg font-bold outline-none focus:ring-2 focus:ring-red-500" />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-bold text-gray-700 mb-1">State</label>
                                        <input required name="state" value={formData.state} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg font-bold outline-none focus:ring-2 focus:ring-red-500" />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-bold text-gray-700 mb-1">Pincode</label>
                                        <input required name="pincode" value={formData.pincode} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg font-bold outline-none focus:ring-2 focus:ring-red-500" />
                                    </div>
                                </div>
                                <div className="pt-6 flex justify-between">
                                    <button type="button" onClick={prevStep} className="px-6 py-3 text-gray-500 font-bold hover:bg-gray-100 rounded-xl transition">
                                        Back
                                    </button>
                                    <button type="button" onClick={nextStep} className="px-8 py-3 bg-red-600 text-white font-bold rounded-xl hover:bg-red-700 transition">
                                        Next : Documents
                                    </button>
                                </div>
                            </div>
                        )}

                        {step === 3 && (
                            <div className="space-y-6 animate-in slide-in-from-right-8 fade-in">
                                <h2 className="text-xl font-bold text-gray-900">Legal & Banking Info</h2>

                                <div className="p-4 bg-yellow-50 rounded-xl border border-yellow-100 mb-4">
                                    <p className="text-sm text-yellow-800 font-medium">⚠️ Please ensure all details match your official documents.</p>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-1">GST Number</label>
                                        <input required name="gst_number" value={formData.gst_number} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg font-bold outline-none focus:ring-2 focus:ring-red-500" />
                                    </div>
                                    <div>
                                        <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-1">PAN Number</label>
                                        <input required name="pan_number" value={formData.pan_number} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg font-bold outline-none focus:ring-2 focus:ring-red-500" />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-1">FSSAI License</label>
                                    <input required name="fssai_license" value={formData.fssai_license} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg font-bold outline-none focus:ring-2 focus:ring-red-500" />
                                </div>

                                <div className="border-t pt-6 mt-6">
                                    <h3 className="text-md font-bold text-gray-900 mb-4">Bank Details (For Payouts)</h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="col-span-2">
                                            <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-1">Bank Name</label>
                                            <input required name="bank_name" value={formData.bank_name} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg font-bold outline-none focus:ring-2 focus:ring-red-500" />
                                        </div>
                                        <div>
                                            <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-1">Account Number</label>
                                            <input required name="bank_account_number" value={formData.bank_account_number} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg font-bold outline-none focus:ring-2 focus:ring-red-500" />
                                        </div>
                                        <div>
                                            <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-1">IFSC Code</label>
                                            <input required name="ifsc_code" value={formData.ifsc_code} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg font-bold outline-none focus:ring-2 focus:ring-red-500" />
                                        </div>
                                    </div>
                                </div>

                                <div className="pt-6 flex justify-between">
                                    <button type="button" onClick={prevStep} className="px-6 py-3 text-gray-500 font-bold hover:bg-gray-100 rounded-xl transition">
                                        Back
                                    </button>
                                    <button type="submit" disabled={loading} className="px-10 py-3 bg-green-600 text-white font-bold rounded-xl shadow-lg hover:bg-green-700 transition transform hover:scale-[1.02]">
                                        {loading ? 'Submitting...' : 'Submit Application'}
                                    </button>
                                </div>
                            </div>
                        )}
                    </form>
                </div>
            </div>
        </div>
    );
};

export default RestaurantOnboarding;
