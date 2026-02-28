import React, { useState } from 'react';
import { API_BASE_URL } from '../config';
import { getMediaImageUrl } from '../utils/mediaImageUrl';

const ImageWithFallback = ({ src, alt, className, type = 'restaurant' }) => {
    const [error, setError] = useState(false);

    const getImageUrl = (imageSrc) => {
        const mediaUrl = getMediaImageUrl(imageSrc);
        if (!mediaUrl) return null;
        if (mediaUrl.startsWith('http')) return mediaUrl;
        if (mediaUrl.startsWith('/media/')) return mediaUrl;
        if (API_BASE_URL && mediaUrl.startsWith('/')) return `${API_BASE_URL}${mediaUrl}`;
        return mediaUrl;
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
