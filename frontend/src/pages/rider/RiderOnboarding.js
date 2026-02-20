import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../../config';
import { FaUser, FaMotorcycle, FaIdCard, FaUniversity, FaCheck, FaCity, FaFileAlt, FaPaperPlane, FaArrowRight } from 'react-icons/fa';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';

const RiderOnboarding = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const token = localStorage.getItem('token_rider');

    // Steps: 1:Personal, 2:City, 3:Vehicle, 4:Docs, 5:Bank, 6:Submit
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [isExistingRider, setIsExistingRider] = useState(false);

    // Form Data State
    const [personal, setPersonal] = useState({ name: '', email: '' });
    const [cityData, setCityData] = useState({ city: 'Himmatnagar' });
    const [vehicle, setVehicle] = useState({ vehicle_number: '', license_number: '', vehicle_type: 'BIKE' });
    const [documents, setDocuments] = useState({ AADHAR_FRONT: null, AADHAR_BACK: null, LICENSE: null, SELFIE_WITH_VEHICLE: null });
    const [bank, setBank] = useState({ account_holder_name: '', account_number: '', ifsc_code: '', bank_name: '' });

    const headers = useMemo(() => ({ Authorization: `Bearer ${token}`, 'X-Role': 'RIDER' }), [token]);

    useEffect(() => {
        // If passed from login
        if (location.state && location.state.step) {
            // Backend step is DB based (0-6). 
            // If step is 0 (Just made), go to 1. 
            // If step is 1 (Personal done), go to 2.
            // If step is 6 (Submitted), go to status.
            const dbStep = location.state.step;
            if (dbStep >= 6) navigate('/rider/status');
            else setStep(dbStep + 1); // Resume next step
        }

        const fetchProgress = async () => {
            try {
                const res = await axios.get(`${API_BASE_URL}/api/rider/profile/`, { headers });
                if (res.data && res.data.length > 0) {
                    const profile = res.data[0];

                    // Critical Status Check
                    if (profile.status === 'APPROVED') { navigate('/rider/dashboard'); return; }
                    if (['UNDER_REVIEW', 'REJECTED', 'BLOCKED'].includes(profile.status) || profile.onboarding_step >= 6) {
                        navigate('/rider/status');
                        return;
                    }

                    // Pre-fill data
                    setPersonal({ name: profile.rider_name || '', email: '' }); // Email might need separate fetch if not in profile serializer
                    setCityData({ city: profile.city || 'Himmatnagar' });
                    setVehicle({
                        vehicle_number: profile.vehicle_number || '',
                        license_number: profile.license_number || '',
                        vehicle_type: profile.vehicle_type || 'BIKE'
                    });
                    // Bank details usually separate endpoint or not exposed fully for security, relying on user to fill or separate fetch
                    // For now we leave bank empty to ensure they verify it

                    // Sync Step if not set by state
                    if (!location.state) {
                        const nextStep = profile.onboarding_step + 1;
                        setStep(nextStep > 6 ? 6 : nextStep);
                    }

                    if (profile.vehicle_number) setIsExistingRider(true);
                }
            } catch (err) {
                console.error("Fetch profile error", err);
            }
        };
        fetchProgress();
    }, [headers, location.state, navigate]);

    // --- HANDLERS ---

    const handleStep1_Personal = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            // Need to update User model mainly
            await axios.post(`${API_BASE_URL}/api/rider/onboarding/update_personal/`, personal, { headers });
            setStep(2);
        } catch (err) { toast.error("Failed to update personal details"); }
        finally { setLoading(false); }
    };

    const handleStep2_City = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/api/rider/onboarding/update_city/`, cityData, { headers });
            setStep(3);
        } catch (err) { toast.error("Failed to update city"); }
        finally { setLoading(false); }
    };

    const handleStep3_Vehicle = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/api/rider/onboarding/update_vehicle/`, vehicle, { headers });
            setStep(4);
        } catch (err) { toast.error("Failed to update vehicle details"); }
        finally { setLoading(false); }
    };

    const handleFileUpload = async (type, file) => {
        const formData = new FormData();
        formData.append('document_type', type);
        formData.append('file', file);

        try {
            await axios.post(`${API_BASE_URL}/api/rider/onboarding/upload_document/`, formData, { headers });
            setDocuments(prev => ({ ...prev, [type]: file }));
            toast.success(`${type.replace('_', ' ')} uploaded!`);
        } catch (err) { toast.error('Upload failed'); }
    };

    const handleStep4_Docs_Next = () => {
        // Validate at least one doc or if existing rider
        if (!isExistingRider && !documents.AADHAR_FRONT && !documents.LICENSE) {
            toast.error("Please upload at least Aadhaar Front or License");
            return;
        }
        setStep(5);
    };

    const handleStep5_Bank = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/api/rider/onboarding/update_bank/`, bank, { headers });
            setStep(6);
        } catch (err) { toast.error("Failed to update bank details"); }
        finally { setLoading(false); }
    };

    const handleStep6_FinalSubmit = async () => {
        setLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/api/rider/onboarding/submit/`, {}, { headers });
            toast.success("Application Submitted!");
            navigate('/rider/status');
        } catch (err) { toast.error("Submission failed"); }
        finally { setLoading(false); }
    };

    // --- RENDER HELPERS ---

    const renderProgressBar = () => (
        <div className="mb-8 relative">
            <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-gray-200">
                <div style={{ width: `${(step / 6) * 100}%` }} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-red-600 transition-all duration-500"></div>
            </div>
            <div className="flex justify-between text-xs font-bold text-gray-400">
                <span>Personal</span>
                <span>Submitting</span>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8 font-jakarta">
            <div className="max-w-3xl mx-auto">
                {renderProgressBar()}

                <div className="bg-white rounded-3xl shadow-xl overflow-hidden p-6 sm:p-10">
                    <div className="flex items-center mb-8">
                        <div className="bg-red-100 p-3 rounded-full text-red-600 mr-4">
                            {step === 1 && <FaUser size={24} />}
                            {step === 2 && <FaCity size={24} />}
                            {step === 3 && <FaMotorcycle size={24} />}
                            {step === 4 && <FaIdCard size={24} />}
                            {step === 5 && <FaUniversity size={24} />}
                            {step === 6 && <FaPaperPlane size={24} />}
                        </div>
                        <h2 className="text-2xl font-black text-gray-900">
                            {step === 1 && 'Personal Details'}
                            {step === 2 && 'Select City'}
                            {step === 3 && 'Vehicle Info'}
                            {step === 4 && 'Upload Documents'}
                            {step === 5 && 'Bank Account'}
                            {step === 6 && 'Review & Submit'}
                        </h2>
                    </div>

                    <AnimatePresence mode="wait">
                        {step === 1 && (
                            <motion.form key="step1" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} onSubmit={handleStep1_Personal} className="space-y-6">
                                <div>
                                    <label className="block font-bold text-gray-700 mb-2">Full Name</label>
                                    <input type="text" value={personal.name} onChange={e => setPersonal({ ...personal, name: e.target.value })} className="w-full p-4 rounded-xl border border-gray-200 focus:border-red-500 outline-none font-medium" placeholder="Enter your full name" required />
                                </div>
                                <div>
                                    <label className="block font-bold text-gray-700 mb-2">Email Address</label>
                                    <input type="email" value={personal.email} onChange={e => setPersonal({ ...personal, email: e.target.value })} className="w-full p-4 rounded-xl border border-gray-200 focus:border-red-500 outline-none font-medium" placeholder="rider@example.com" required />
                                </div>
                                <button type="submit" disabled={loading} className="w-full bg-red-600 text-white font-bold py-4 rounded-xl hover:bg-red-700 transition flex items-center justify-center">
                                    {loading ? 'Saving...' : <>Next Step <FaArrowRight className="ml-2" /></>}
                                </button>
                            </motion.form>
                        )}

                        {step === 2 && (
                            <motion.form key="step2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} onSubmit={handleStep2_City} className="space-y-6">
                                <div>
                                    <label className="block font-bold text-gray-700 mb-2">Select Your City</label>
                                    <select value={cityData.city} onChange={e => setCityData({ city: e.target.value })} className="w-full p-4 rounded-xl border border-gray-200 focus:border-red-500 outline-none font-medium">
                                        <option value="Himmatnagar">Himmatnagar</option>
                                        <option value="Mehsana">Mehsana</option>
                                        <option value="Ahmedabad">Ahmedabad</option>
                                        <option value="Gandhinagar">Gandhinagar</option>
                                    </select>
                                    <p className="text-sm text-gray-500 mt-2">Note: You can only accept orders within this city.</p>
                                </div>
                                <div className="flex gap-4">
                                    <button type="button" onClick={() => setStep(1)} className="w-1/3 bg-gray-100 text-gray-600 font-bold py-4 rounded-xl hover:bg-gray-200 transition">Back</button>
                                    <button type="submit" disabled={loading} className="w-2/3 bg-red-600 text-white font-bold py-4 rounded-xl hover:bg-red-700 transition flex items-center justify-center">
                                        {loading ? 'Saving...' : <>Next Step <FaArrowRight className="ml-2" /></>}
                                    </button>
                                </div>
                            </motion.form>
                        )}

                        {step === 3 && (
                            <motion.form key="step3" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} onSubmit={handleStep3_Vehicle} className="space-y-6">
                                <div className="grid grid-cols-2 gap-4">
                                    <div className={`p-4 rounded-xl border-2 cursor-pointer text-center transition ${vehicle.vehicle_type === 'BIKE' ? 'border-red-500 bg-red-50 text-red-600' : 'border-gray-200'}`} onClick={() => setVehicle({ ...vehicle, vehicle_type: 'BIKE' })}>
                                        <FaMotorcycle size={32} className="mx-auto mb-2" />
                                        <span className="font-bold">Bike</span>
                                    </div>
                                    <div className={`p-4 rounded-xl border-2 cursor-pointer text-center transition ${vehicle.vehicle_type === 'SCOOTER' ? 'border-red-500 bg-red-50 text-red-600' : 'border-gray-200'}`} onClick={() => setVehicle({ ...vehicle, vehicle_type: 'SCOOTER' })}>
                                        <FaMotorcycle size={32} className="mx-auto mb-2" />
                                        <span className="font-bold">Scooter</span>
                                    </div>
                                </div>
                                <div>
                                    <label className="block font-bold text-gray-700 mb-2">Vehicle Number</label>
                                    <input type="text" value={vehicle.vehicle_number} onChange={e => setVehicle({ ...vehicle, vehicle_number: e.target.value.toUpperCase() })} className="w-full p-4 rounded-xl border border-gray-200 focus:border-red-500 outline-none font-medium uppercase" placeholder="GJ01AB1234" required />
                                </div>
                                <div>
                                    <label className="block font-bold text-gray-700 mb-2">Driving License Number</label>
                                    <input type="text" value={vehicle.license_number} onChange={e => setVehicle({ ...vehicle, license_number: e.target.value.toUpperCase() })} className="w-full p-4 rounded-xl border border-gray-200 focus:border-red-500 outline-none font-medium uppercase" placeholder="GJ0120220001234" required />
                                </div>
                                <div className="flex gap-4">
                                    <button type="button" onClick={() => setStep(2)} className="w-1/3 bg-gray-100 text-gray-600 font-bold py-4 rounded-xl hover:bg-gray-200 transition">Back</button>
                                    <button type="submit" disabled={loading} className="w-2/3 bg-red-600 text-white font-bold py-4 rounded-xl hover:bg-red-700 transition flex items-center justify-center">
                                        {loading ? 'Saving...' : <>Next Step <FaArrowRight className="ml-2" /></>}
                                    </button>
                                </div>
                            </motion.form>
                        )}

                        {step === 4 && (
                            <motion.div key="step4" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-6">
                                {[
                                    { id: 'AADHAR_FRONT', label: 'Aadhaar Card Front' },
                                    { id: 'AADHAR_BACK', label: 'Aadhaar Card Back' },
                                    { id: 'LICENSE', label: 'Driving License' },
                                    { id: 'SELFIE_WITH_VEHICLE', label: 'Selfie with Vehicle' }
                                ].map((doc) => (
                                    <div key={doc.id} className="border-2 border-dashed border-gray-300 rounded-xl p-4 flex items-center justify-between hover:border-red-500 transition relative bg-gray-50">
                                        <div className="flex items-center">
                                            <div className="bg-white p-3 rounded-lg border border-gray-200 mr-4">
                                                <FaFileAlt className="text-gray-400 text-xl" />
                                            </div>
                                            <div>
                                                <p className="font-bold text-gray-700 text-sm">{doc.label}</p>
                                                {documents[doc.id] ? <p className="text-green-600 text-xs font-bold mt-1 flex items-center"><FaCheck className="mr-1" /> Uploaded</p> : <p className="text-gray-400 text-xs mt-1">Required</p>}
                                            </div>
                                        </div>
                                        <label className="bg-white text-gray-700 font-bold text-xs py-2 px-4 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-50 shadow-sm">
                                            {documents[doc.id] ? 'Change' : 'Upload'}
                                            <input type="file" onChange={(e) => handleFileUpload(doc.id, e.target.files[0])} className="hidden" accept="image/*" />
                                        </label>
                                    </div>
                                ))}
                                <div className="flex gap-4">
                                    <button type="button" onClick={() => setStep(3)} className="w-1/3 bg-gray-100 text-gray-600 font-bold py-4 rounded-xl hover:bg-gray-200 transition">Back</button>
                                    <button onClick={handleStep4_Docs_Next} className="w-2/3 bg-red-600 text-white font-bold py-4 rounded-xl hover:bg-red-700 transition flex items-center justify-center">
                                        Next Step <FaArrowRight className="ml-2" />
                                    </button>
                                </div>
                            </motion.div>
                        )}

                        {step === 5 && (
                            <motion.form key="step5" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} onSubmit={handleStep5_Bank} className="space-y-6">
                                <div>
                                    <label className="block font-bold text-gray-700 mb-2">Account Holder Name</label>
                                    <input type="text" value={bank.account_holder_name} onChange={e => setBank({ ...bank, account_holder_name: e.target.value })} className="w-full p-4 rounded-xl border border-gray-200 focus:border-red-500 outline-none font-medium" required />
                                </div>
                                <div>
                                    <label className="block font-bold text-gray-700 mb-2">Account Number</label>
                                    <input type="text" value={bank.account_number} onChange={e => setBank({ ...bank, account_number: e.target.value })} className="w-full p-4 rounded-xl border border-gray-200 focus:border-red-500 outline-none font-medium" required />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block font-bold text-gray-700 mb-2">IFSC Code</label>
                                        <input type="text" value={bank.ifsc_code} onChange={e => setBank({ ...bank, ifsc_code: e.target.value.toUpperCase() })} className="w-full p-4 rounded-xl border border-gray-200 focus:border-red-500 outline-none font-medium uppercase" required />
                                    </div>
                                    <div>
                                        <label className="block font-bold text-gray-700 mb-2">Bank Name</label>
                                        <input type="text" value={bank.bank_name} onChange={e => setBank({ ...bank, bank_name: e.target.value })} className="w-full p-4 rounded-xl border border-gray-200 focus:border-red-500 outline-none font-medium" required />
                                    </div>
                                </div>
                                <div className="flex gap-4">
                                    <button type="button" onClick={() => setStep(4)} className="w-1/3 bg-gray-100 text-gray-600 font-bold py-4 rounded-xl hover:bg-gray-200 transition">Back</button>
                                    <button type="submit" disabled={loading} className="w-2/3 bg-red-600 text-white font-bold py-4 rounded-xl hover:bg-red-700 transition flex items-center justify-center">
                                        {loading ? 'Saving...' : <>Review & Submit <FaArrowRight className="ml-2" /></>}
                                    </button>
                                </div>
                            </motion.form>
                        )}

                        {step === 6 && (
                            <motion.div key="step6" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="text-center space-y-8">
                                <div className="bg-green-50 p-6 rounded-2xl border border-green-100 inline-block">
                                    <FaCheckCircleSize className="text-green-500" />
                                </div>
                                <div>
                                    <h3 className="text-2xl font-black text-gray-900 mb-2">All Set!</h3>
                                    <p className="text-gray-500">You are ready to submit your application for review.</p>
                                </div>

                                <div className="bg-gray-50 rounded-xl p-6 text-left space-y-3">
                                    <div className="flex justify-between border-b pb-2">
                                        <span className="text-gray-500">Name</span>
                                        <span className="font-bold">{personal.name}</span>
                                    </div>
                                    <div className="flex justify-between border-b pb-2">
                                        <span className="text-gray-500">City</span>
                                        <span className="font-bold">{cityData.city}</span>
                                    </div>
                                    <div className="flex justify-between border-b pb-2">
                                        <span className="text-gray-500">Vehicle</span>
                                        <span className="font-bold">{vehicle.vehicle_type} - {vehicle.vehicle_number}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-500">Bank</span>
                                        <span className="font-bold">{bank.bank_name}</span>
                                    </div>
                                </div>

                                <div className="flex gap-4">
                                    <button type="button" onClick={() => setStep(5)} className="w-1/3 bg-gray-100 text-gray-600 font-bold py-4 rounded-xl hover:bg-gray-200 transition">Back</button>
                                    <button onClick={handleStep6_FinalSubmit} disabled={loading} className="w-2/3 bg-black text-white font-bold py-4 rounded-xl hover:bg-gray-800 transition shadow-xl">
                                        {loading ? 'Submitting...' : 'Submit Application'}
                                    </button>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
};

const FaCheckCircleSize = () => <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center"><FaCheck className="text-green-600 text-2xl" /></div>;

export default RiderOnboarding;
