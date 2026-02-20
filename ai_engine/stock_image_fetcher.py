"""
Stock Image Fetcher for automatic dish image assignment.
Uses free stock photo APIs (Pexels) to fetch and assign food images.
"""

import requests
import time
from decouple import config
from django.core.files.base import ContentFile
from client.models import MenuItem


class StockImageFetcher:
    """Fetches food images from stock photo APIs and assigns to dishes."""
    
    def __init__(self):
        self.pexels_api_key = config('PEXELS_API_KEY', default=None)
        self.pexels_url = "https://api.pexels.com/v1/search"
    
    def generate_search_keyword(self, dish):
        """
        Convert dish name to search-friendly keyword.
        
        Examples:
            "Paneer Butter Masala" → "paneer butter masala food"
            "Chicken Biryani" → "chicken biryani food"
        """
        dish_name = dish.name.lower().strip()
        
        # Add "food" suffix for better results
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
    
    def fetch_image_from_pexels(self, keyword):
        """
        Fetch image URL from Pexels API.
        
        Args:
            keyword: Search keyword
            
        Returns:
            Image URL (string) or None if not found
        """
        if not self.pexels_api_key:
            print("Warning: PEXELS_API_KEY not configured")
            return None
        
        try:
            headers = {
                'Authorization': self.pexels_api_key
            }
            
            params = {
                'query': keyword,
                'per_page': 1,
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
                    # Get medium-sized image (good balance of quality and size)
                    photo = data['photos'][0]
                    image_url = photo['src'].get('medium', photo['src'].get('original'))
                    return image_url
                else:
                    print(f"No photos found for keyword: {keyword}")
                    return None
            else:
                print(f"Pexels API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error fetching from Pexels: {e}")
            return None
    
    def download_and_save(self, image_url, dish_id):
        """
        Download image from URL and return ContentFile for saving.
        
        Args:
            image_url: URL of the image
            dish_id: ID of the dish
            
        Returns:
            ContentFile or None if download fails
        """
        if not image_url:
            return None
        
        try:
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                file_name = f"dish_{dish_id}.jpg"
                return ContentFile(response.content, name=f"dishes/{file_name}")
            else:
                print(f"Failed to download image: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None
    
    def process_single(self, dish_id):
        """
        Process a single dish by ID.
        
        Args:
            dish_id: ID of the dish to process
            
        Returns:
            dict with status and message
        """
        try:
            dish = MenuItem.objects.get(id=dish_id)
            
            # Skip if already has image
            if dish.image:
                return {'success': False, 'message': 'Dish already has image'}
            
            # Generate keywords
            primary_keyword, fallback_keywords = self.generate_search_keyword(dish)
            
            # Try primary keyword first
            image_url = self.fetch_image_from_pexels(primary_keyword)
            
            # Try fallback keywords if primary fails
            if not image_url:
                for fallback in fallback_keywords:
                    print(f"Trying fallback keyword: {fallback}")
                    image_url = self.fetch_image_from_pexels(fallback)
                    if image_url:
                        break
            
            if not image_url:
                return {'success': False, 'message': 'No image found'}
            
            # Download and save
            image_content = self.download_and_save(image_url, dish.id)
            
            if image_content:
                dish.image = image_content
                dish.save()
                return {'success': True, 'message': f'Image assigned for {dish.name}'}
            else:
                return {'success': False, 'message': 'Failed to download image'}
                
        except MenuItem.DoesNotExist:
            return {'success': False, 'message': 'Dish not found'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def process_batch(self, limit=20, dry_run=False):
        """
        Process multiple dishes in batch.
        
        Args:
            limit: Maximum number of dishes to process
            dry_run: If True, simulate without making API calls
            
        Returns:
            dict with results summary
        """
        # Get dishes without images
        dishes = MenuItem.objects.filter(image='').order_by('id')[:limit]
        
        results = {
            'total': dishes.count(),
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        print(f"Found {results['total']} dishes to process.")
        
        for dish in dishes:
            print(f"Processing Dish ID {dish.id}: {dish.name}...")
            
            if dry_run:
                # Just show what would be done
                primary_keyword, fallback_keywords = self.generate_search_keyword(dish)
                print(f"[DRY RUN] Would search for: {primary_keyword}")
                print(f"[DRY RUN] Fallbacks: {fallback_keywords}")
                results['success'] += 1
                continue
            
            try:
                # Generate keywords
                primary_keyword, fallback_keywords = self.generate_search_keyword(dish)
                
                # Try primary keyword
                image_url = self.fetch_image_from_pexels(primary_keyword)
                
                # Try fallbacks if needed
                if not image_url:
                    for fallback in fallback_keywords:
                        print(f"  Trying fallback: {fallback}")
                        image_url = self.fetch_image_from_pexels(fallback)
                        if image_url:
                            break
                
                if image_url:
                    # Download and save
                    image_content = self.download_and_save(image_url, dish.id)
                    
                    if image_content:
                        dish.image = image_content
                        dish.save()
                        results['success'] += 1
                        print(f"  [+] Successfully assigned image to {dish.name}")
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Failed to download image for {dish.name}")
                else:
                    results['failed'] += 1
                    results['errors'].append(f"No image found for {dish.name}")
                
                # Rate limiting: sleep 1 second between requests (well under 200/hour limit)
                time.sleep(1)
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error processing {dish.name}: {str(e)}")
                print(f"  [x] Error: {e}")
        
        return results
