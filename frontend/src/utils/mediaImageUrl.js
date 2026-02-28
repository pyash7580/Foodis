/**
 * Resolve image URLs so that cover, logo, and dish images load from
 * frontend/public/media (served at /media/... from same origin).
 * Add your images to: frontend/public/media/restaurants/, public/media/menu_items/, etc.
 */

/**
 * Returns the URL to use for <img src={...}>.
 * - Paths starting with /media/ are kept as-is so the browser loads from
 *   the frontend origin (React dev server or static build), which serves
 *   files from public/media. Place files in frontend/public/media/.
 * - Full http(s) URLs are returned as-is.
 * - Other relative paths can be normalized to /media/... if needed.
 * @param {string} imageUrl - URL from API (e.g. /media/restaurants/logo.jpg) or full URL
 * @returns {string|null} URL to use for img src
 */
export function getMediaImageUrl(imageUrl) {
    if (!imageUrl || typeof imageUrl !== 'string') return null;
    const s = imageUrl.trim();
    if (!s) return null;
    // Already absolute
    if (s.startsWith('http://') || s.startsWith('https://')) return s;
    // Frontend public/media: serve from same origin (public/media/...)
    if (s.startsWith('/media/')) return s;
    // Backend-relative path without leading slash: treat as under /media/
    if (s.startsWith('media/') || s.startsWith('restaurants/') || s.startsWith('menu_items/')) {
        return s.startsWith('media/') ? `/${s}` : `/media/${s}`;
    }
    return s;
}
