from difflib import get_close_matches

def normalize_city_name(city_name):
    """
    Normalizes city names to handle regional variations and synonyms.
    Uses exact matching first, then falls back to fuzzy matching if needed.
    E.g., mapping 'Sabarkantha', 'H', or 'Himatnagar' to 'Himmatnagar'.
    """
    if not city_name:
        return city_name

    name = city_name.strip().title()

    # Exact mapping variants to standardized city names
    exact_mapping = {
        'H': 'Himmatnagar',
        'Himmat Nagar': 'Himmatnagar',
        'Himmat-Nagar': 'Himmatnagar',
        'Sabarkantha': 'Himmatnagar',
        'Sabar Kantha': 'Himmatnagar',
        'M': 'Mehsana',
        'Mehsana ': 'Mehsana',
        'Mehsanaa': 'Mehsana',
        'Mahesana': 'Mehsana',
    }

    # Try exact match first
    if name in exact_mapping:
        return exact_mapping[name]

    # Fuzzy matching as fallback
    standard_cities = ['Himmatnagar', 'Mehsana']
    close_matches = get_close_matches(name, standard_cities, n=1, cutoff=0.6)

    if close_matches:
        return close_matches[0]

    # If no fuzzy match, return original normalized name
    return name

