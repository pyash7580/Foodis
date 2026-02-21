
import React, { useState, useEffect, useCallback } from 'react';

const LocationDetector = ({ onLocationDetected }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [location, setLocation] = useState('Detecting location...');
    const [error, setError] = useState('');

    const detectLocation = useCallback(() => {
        setIsLoading(true);
        setIsOpen(false);
        setLocation('Detecting...');
        setError('');

        if (!navigator.geolocation) {
            setError('Geolocation is not supported');
            setLocation('Location unavailable');
            setIsLoading(false);
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                // Mock Reverse Geocoding
                setLocation('Current Location');
                setIsLoading(false);
                if (onLocationDetected) {
                    onLocationDetected({ latitude, longitude });
                }
            },
            (err) => {
                console.warn('Geolocation:', err.message);
                setError('Permission denied or unavailable');
                setLocation('Select Location');
                setIsLoading(false);
            },
            { timeout: 10000 }
        );
    }, [onLocationDetected]);

    useEffect(() => {
        detectLocation();
    }, [detectLocation]);

    return (
        <div className="relative">
            <div className="flex items-center text-gray-700">
                <span className="mr-2 text-red-600 text-xl">📍</span>
                <div>
                    <p className="text-xs text-gray-500 font-bold uppercase tracking-wider">Delivering to</p>
                    <div
                        className="flex items-center cursor-pointer hover:text-red-600"
                        onClick={() => setIsOpen(!isOpen)}
                    >
                        <span className="font-bold text-sm sm:text-base truncate max-w-[150px]">
                            {location}
                        </span>
                        <span className="ml-1 text-xs">▼</span>
                    </div>
                </div>
            </div>

            {/* Dropdown Menu */}
            {isOpen && (
                <div className="absolute top-full left-0 mt-2 w-56 bg-white rounded-md shadow-lg py-1 z-50 ring-1 ring-black ring-opacity-5">
                    <button
                        onClick={detectLocation}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                    >
                        <span className="mr-2">🎯</span> Detect Current Location
                    </button>
                    <button
                        onClick={() => {
                            setLocation('Mehsana');
                            setIsOpen(false);
                            if (onLocationDetected) {
                                onLocationDetected({ city: 'Mehsana' });
                            }
                        }}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                    >
                        <span className="mr-2">🏛️</span> Mehsana
                    </button>
                    <button
                        onClick={() => {
                            setLocation('Himmatnagar');
                            setIsOpen(false);
                            if (onLocationDetected) {
                                onLocationDetected({ city: 'Himmatnagar' });
                            }
                        }}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                    >
                        <span className="mr-2">🏘️</span> Himmatnagar
                    </button>
                </div>
            )}

            {error && !isLoading && isOpen && (
                <div className="absolute top-full left-0 mt-32 w-56 px-2">
                    <p className="text-xs text-red-500 bg-red-50 p-1 rounded">⚠️ {error}</p>
                </div>
            )}
        </div>
    );
};

export default LocationDetector;
