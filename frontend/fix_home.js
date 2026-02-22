const fs = require('fs');
const filepath = 'src/pages/client/Home.js';

let content = fs.readFileSync(filepath, 'utf8');

const target2 = `    const fetchRestaurants = useCallback(async () => {
        // Build URL with city filter if selected
        let url = \`\${API_BASE_URL}/api/client/restaurants/\`;
        if (selectedCity) {
            url += \`?city=\${encodeURIComponent(selectedCity)}\`;
        }

        try {
            setLoading(true);
            const config = token ? { headers: { Authorization: \`Bearer \${token}\`, 'X-Role': 'CLIENT' } } : {};
            const response = await axios.get(url, config);
            let data = response.data.results || response.data;

            // Fallback: if a strict city filter returns empty, retry without city
            // so users still see available restaurants.
            if (selectedCity && Array.isArray(data) && data.length === 0) {`;

const replacement2 = `    const fetchRestaurants = useCallback(async () => {
        // Build URL with city filter if selected
        let url = \`\${API_BASE_URL}/api/client/restaurants/\`;
        let params = new URLSearchParams();
        
        if (selectedCity) {
            params.append('city', selectedCity);
        } else if (userLocation) {
            params.append('latitude', userLocation.latitude);
            params.append('longitude', userLocation.longitude);
        }
        
        const queryString = params.toString();
        if (queryString) {
            url += \`?\${queryString}\`;
        }

        try {
            setLoading(true);
            const config = token ? { headers: { Authorization: \`Bearer \${token}\`, 'X-Role': 'CLIENT' } } : {};
            const response = await axios.get(url, config);
            let data = response.data.results || response.data;

            // Fallback: if a strict city/location filter returns empty, retry without filters
            // so users still see available restaurants.
            if ((selectedCity || userLocation) && Array.isArray(data) && data.length === 0) {`;

if (content.includes(target2)) content = content.replace(target2, replacement2);

fs.writeFileSync(filepath, content);
console.log('Replacements applied successfully!');
