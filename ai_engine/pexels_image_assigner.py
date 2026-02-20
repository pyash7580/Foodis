"""
Enhanced Stock Image Fetcher for automatic dish image assignment.
Uses Pexels API to fetch and assign food image URLs to dishes.
Production-ready with caching, validation, and comprehensive error handling.
"""

import requests
import time
from decouple import config
from django.core.cache import cache
from django.core.files.base import ContentFile
from client.models import MenuItem
import hashlib


class PexelsImageAssigner:
    """
    Assigns food images from Pexels API to dishes.
    Stores URLs only (no file download) with caching and validation.
    """
    
    def __init__(self):
        self.pexels_api_key = config('PEXELS_API_KEY', default=None)
        self.pexels_url = "https://api.pexels.com/v1/search"
        self.cache_timeout = 86400 * 7  # 7 days
        
    def _get_cache_key(self, dish_name):
        """Generate cache key from dish name."""
        normalized_name = dish_name.lower().strip()
        return f"pexels_image_{hashlib.md5(normalized_name.encode()).hexdigest()}"
    
    def generate_search_keyword(self, dish):
        """
        Convert dish name to search-friendly keyword.
        
        Examples:
            "Paneer Butter Masala" → "paneer butter masala food"
            "Chicken Biryani" → "chicken biryani food"
        """
        dish_name = dish.name.lower().strip()
        
        # Primary keyword with "food" suffix
        primary_keyword = f"{dish_name} food"
        
        # Generate fallback keywords
        fallback_keywords = []
        
        # Try category if available
        if dish.category:
            fallback_keywords.append(f"{dish.category.name.lower()} food")
        
        # Try cuisine type if available
        if dish.restaurant and hasattr(dish.restaurant, 'cuisine') and dish.restaurant.cuisine:
            fallback_keywords.append(f"{dish.restaurant.cuisine.lower()} food")
        
        # Generic fallback
        fallback_keywords.append("delicious food")
        
        return primary_keyword, fallback_keywords
    
    def select_best_image(self, photos):
        """
        Select the best image from multiple results based on:
        - Landscape or square orientation (better for food cards)
        - Higher resolution
        - Professional quality indicators
        
        Args:
            photos: List of photo objects from Pexels API
            
        Returns:
            Best photo object or None
        """
        if not photos:
            return None
        
        # Score each photo
        scored_photos = []
        for photo in photos:
            score = 0
            width = photo.get('width', 0)
            height = photo.get('height', 0)
            
            # Prefer landscape or square orientation
            if width >= height:
                score += 2
            
            # Prefer higher resolution (but not extremely high)
            resolution = width * height
            if 500000 <= resolution <= 2000000:  # Sweet spot for web images
                score += 3
            elif resolution > 2000000:
                score += 1
            
            # Prefer images with photographer attribution (quality indicator)
            if photo.get('photographer'):
                score += 1
            
            scored_photos.append((score, photo))
        
        # Return highest scored photo
        scored_photos.sort(key=lambda x: x[0], reverse=True)
        return scored_photos[0][1] if scored_photos else None
    
    def validate_image_url(self, url):
        """
        Validate image URL:
        - HTTP 200 response
        - Supported format (jpg, png, webp)
        - Not a watermarked preview
        
        Args:
            url: Image URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not url:
            return False
        
        try:
            # Check format
            url_lower = url.lower()
            if not any(fmt in url_lower for fmt in ['.jpg', '.jpeg', '.png', '.webp']):
                print(f"  [!] Unsupported format: {url}")
                return False
            
            # Avoid tiny previews and watermarked images
            if 'tiny' in url_lower or 'watermark' in url_lower:
                print(f"  [!] Watermarked or tiny image: {url}")
                return False
            
            # Check HTTP 200
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                return True
            else:
                print(f"  [!] HTTP {response.status_code} for URL: {url}")
                return False
                
        except Exception as e:
            print(f"  [!] Validation error for {url}: {e}")
            return False
    
    def fetch_best_image_from_pexels(self, keyword, per_page=5):
        """
        Fetch multiple results and select the best one based on relevance criteria.
        
        Args:
            keyword: Search keyword
            per_page: Number of results to fetch (max 5 for selection)
            
        Returns:
            Best image URL or None
        """
        if not self.pexels_api_key:
            print("  [!] PEXELS_API_KEY not configured")
            return None
        
        try:
            headers = {
                'Authorization': self.pexels_api_key
            }
            
            params = {
                'query': keyword,
                'per_page': per_page,
                'orientation': 'landscape'  # Better for food photos
            }
            
            response = requests.get(
                self.pexels_url,
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('photos') and len(data['photos']) > 0:
                    # Select best photo from results
                    best_photo = self.select_best_image(data['photos'])
                    if best_photo:
                        # Get medium-sized image (good balance of quality and size)
                        image_url = best_photo['src'].get('medium', best_photo['src'].get('original'))
                        
                        # Validate URL before returning
                        if self.validate_image_url(image_url):
                            return image_url
                        else:
                            print(f"  [!] Best image failed validation, trying original...")
                            # Try original as backup
                            original_url = best_photo['src'].get('original')
                            if self.validate_image_url(original_url):
                                return original_url
                    
                    print(f"  [!] No suitable photos found for keyword: {keyword}")
                    return None
                else:
                    print(f"  [!] No photos found for keyword: {keyword}")
                    return None
            else:
                print(f"  [!] Pexels API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"  [!] Error fetching from Pexels: {e}")
            return None
    
    def assign_image_url_to_dish(self, dish, force=False):
        """
        Assign image URL to dish without downloading.
        Uses cache to ensure consistency for same dish names.
        
        Args:
            dish: MenuItem instance
            force: If True, override existing image_url
            
        Returns:
            dict with status and message
        """
        try:
            # Skip if already has image_url (unless forced)
            if dish.image_url and not force:
                return {
                    'success': False,
                    'status': 'skipped',
                    'message': f'Dish already has image_url: {dish.name}',
                    'dish_id': dish.id,
                    'dish_name': dish.name
                }
            
            # Check cache first
            cache_key = self._get_cache_key(dish.name)
            cached_url = cache.get(cache_key)
            
            if cached_url:
                # Use cached URL
                dish.image_url = cached_url
                dish.save(update_fields=['image_url'])
                return {
                    'success': True,
                    'status': 'cached',
                    'message': f'Assigned cached image to: {dish.name}',
                    'dish_id': dish.id,
                    'dish_name': dish.name,
                    'image_url': cached_url
                }
            
            # Generate keywords
            primary_keyword, fallback_keywords = self.generate_search_keyword(dish)
            
            # Try primary keyword first
            image_url = self.fetch_best_image_from_pexels(primary_keyword)
            
            # Try fallback keywords if primary fails
            if not image_url:
                for fallback in fallback_keywords:
                    print(f"  → Trying fallback: {fallback}")
                    image_url = self.fetch_best_image_from_pexels(fallback)
                    if image_url:
                        break
            
            if not image_url:
                return {
                    'success': False,
                    'status': 'not_found',
                    'message': f'No image found for: {dish.name}',
                    'dish_id': dish.id,
                    'dish_name': dish.name
                }
            
            # Save to database
            dish.image_url = image_url
            dish.save(update_fields=['image_url'])
            
            # Cache the result
            cache.set(cache_key, image_url, self.cache_timeout)
            
            return {
                'success': True,
                'status': 'assigned',
                'message': f'Successfully assigned image to: {dish.name}',
                'dish_id': dish.id,
                'dish_name': dish.name,
                'image_url': image_url
            }
            
        except Exception as e:
            return {
                'success': False,
                'status': 'error',
                'message': f'Error processing {dish.name}: {str(e)}',
                'dish_id': dish.id if hasattr(dish, 'id') else None,
                'dish_name': dish.name if hasattr(dish, 'name') else 'Unknown'
            }
    
    def process_batch(self, queryset, dry_run=False, rate_limit_seconds=1):
        """
        Process multiple dishes in batch.
        
        Args:
            queryset: QuerySet of MenuItem objects
            dry_run: If True, simulate without making API calls
            rate_limit_seconds: Seconds to wait between API requests
            
        Returns:
            dict with comprehensive results summary
        """
        results = {
            'total': queryset.count(),
            'processed': 0,
            'images_added': 0,
            'skipped': 0,
            'cached': 0,
            'not_found': 0,
            'errors': 0,
            'warnings': [],
            'error_details': [],
            'api_calls': 0,
            'start_time': time.time()
        }
        
        print(f"\n{'='*60}")
        print(f"Processing {results['total']} dishes...")
        print(f"{'='*60}\n")
        
        for dish in queryset:
            print(f"[{results['processed'] + 1}/{results['total']}] Processing: {dish.name} (ID: {dish.id})")
            
            if dry_run:
                # Just show what would be done
                primary_keyword, fallback_keywords = self.generate_search_keyword(dish)
                print(f"  [DRY RUN] Would search: {primary_keyword}")
                print(f"  [DRY RUN] Fallbacks: {', '.join(fallback_keywords)}")
                results['processed'] += 1
                continue
            
            try:
                result = self.assign_image_url_to_dish(dish, force=False)
                results['processed'] += 1
                
                if result['success']:
                    if result['status'] == 'cached':
                        results['cached'] += 1
                        print(f"  [OK] Cached: {result['image_url']}")
                    else:
                        results['images_added'] += 1
                        results['api_calls'] += 1
                        print(f"  [OK] Assigned: {result['image_url']}")
                else:
                    if result['status'] == 'skipped':
                        results['skipped'] += 1
                        print(f"  [->] Skipped (already has image)")
                    elif result['status'] == 'not_found':
                        results['not_found'] += 1
                        results['warnings'].append(f"No Image Found – {dish.name}")
                        print(f"  [!] No image found")
                    else:
                        results['errors'] += 1
                        results['error_details'].append(result['message'])
                        print(f"  [X] Error: {result['message']}")
                
                # Rate limiting (only for actual API calls, not cache hits)
                if not dry_run and result.get('status') != 'cached' and result.get('status') != 'skipped':
                    time.sleep(rate_limit_seconds)
                
            except Exception as e:
                results['errors'] += 1
                results['error_details'].append(f"Exception for {dish.name}: {str(e)}")
                print(f"  [X] Exception: {e}")
        
        # Calculate total time
        results['end_time'] = time.time()
        results['duration'] = results['end_time'] - results['start_time']
        
        return results
