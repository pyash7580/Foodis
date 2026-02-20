def normalize_city_name(city_name):
    """
    Normalizes city names to handle regional variations and synonyms.
    E.g., mapping 'Sabarkantha' or 'H' to 'Himmatnagar'.
    """
    if not city_name:
        return city_name
        
    name = city_name.strip().title()
    
    # Mapping variants to standardized city names
    mapping = {
        'H': 'Himmatnagar',
        'Himmat Nagar': 'Himmatnagar',
        'Sabarkantha': 'Himmatnagar',
        'M': 'Mehsana',
        'Mehsana ': 'Mehsana',
    }
    
    return mapping.get(name, name)
