
// Curated list of high-quality food images from Unsplash
export const FOOD_IMAGES = [
    "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80",
    "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=800&q=80",
    "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800&q=80",
    "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=800&q=80",
    "https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=800&q=80",
    "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?w=800&q=80",
    "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80",
    "https://images.unsplash.com/photo-1484723091739-30a097e8f929?w=800&q=80",
    "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800&q=80",
    "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&q=80",
    "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=800&q=80",
    "https://images.unsplash.com/photo-1585937421612-70a008356f36?w=800&q=80",
    "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&q=80",
    "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=800&q=80",
    "https://images.unsplash.com/photo-1563379926898-05f4575a45d8?w=800&q=80",
    "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&q=80",
];

export const COVER_IMAGES = [
    "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&q=80",
    "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=1200&q=80",
    "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=1200&q=80",
    "https://images.unsplash.com/photo-1514362545857-3bc16549766b?w=1200&q=80",
    "https://images.unsplash.com/photo-1590846406792-0adc7f938f1d?w=1200&q=80",
];

export const getRestaurantImage = (id) => FOOD_IMAGES[id % FOOD_IMAGES.length];
export const getRestaurantCover = (id) => COVER_IMAGES[id % COVER_IMAGES.length];
