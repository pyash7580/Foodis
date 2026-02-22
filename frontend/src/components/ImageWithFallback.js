import React, { useState } from 'react';

const ImageWithFallback = ({ src, alt, className, type = 'restaurant' }) => {
    const [error, setError] = useState(false);

    if (!src || error) {
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
            src={src}
            alt={alt || 'Food image'}
            className={className}
            loading="lazy"
            onError={() => setError(true)}
        />
    );
};

export default ImageWithFallback;
