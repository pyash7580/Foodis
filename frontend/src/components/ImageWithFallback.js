import React, { useState } from 'react';
import { API_BASE_URL } from '../config';

const ImageWithFallback = ({ src, alt, className, type = 'restaurant' }) => {
    const [error, setError] = useState(false);

    // Helper function to get proper image URL
    const getImageUrl = (imageSrc) => {
        if (!imageSrc) return null;
        
        // If already absolute URL, return as-is
        if (imageSrc.startsWith('http://') || imageSrc.startsWith('https://')) {
            return imageSrc;
        }
        
        // If relative path and we have API base URL, prepend it
        if (imageSrc.startsWith('/') && API_BASE_URL) {
            return `${API_BASE_URL}${imageSrc}`;
        }
        
        // Return as-is (works with local proxy)
        return imageSrc;
    };

    const imageUrl = getImageUrl(src);

    if (!imageUrl || error) {
        return (
            <div className={`${className} bg-gray-100 flex items-center justify-center`}>
                <div className="text-center text-gray-400">
                    <span className="text-4xl">{type === 'dish' ? '🍲' : '🍽️'}</span>
                    <p className="text-[10px] mt-1 font-bold uppercase tracking-wider">No Image</p>
                </div>
            </div>
        );
    }

    return (
        <img
            src={imageUrl}
            alt={alt || 'Food image'}
            className={className}
            loading="lazy"
            onError={() => setError(true)}
        />
    );
};

export default ImageWithFallback;
