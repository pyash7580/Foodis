import os
import sys
import django
import requests
import time
from decouple import config
from django.core.files.base import ContentFile
import uuid

# Add current directory to sys.path
sys.path.append(os.getcwd())

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import Restaurant

class RestaurantCoverUpdater:
    def __init__(self):
        self.api_key = config('PEXELS_API_KEY', default=None)
        self.search_url = "https://api.pexels.com/v1/search"
        self.headers = {'Authorization': self.api_key} if self.api_key else {}
        self.media_path = os.path.join('restaurants', 'covers')
        
        if not self.api_key:
            print("CRITICAL: PEXELS_API_KEY not found in .env")

    def get_search_query(self, restaurant):
        """Generate a realistic search query based on restaurant name and cuisine."""
        name = restaurant.name.lower()
        cuisine = restaurant.cuisine.lower() if restaurant.cuisine else ""
        
        # Priority 1: Specific restaurant type based on name keywords
        if "cafe" in name:
            return "aesthetic cafe interior"
        if "biryani" in name or "kebabs" in name:
            return "indian luxury restaurant interior"
        if "bakery" in name or "dessert" in name or "sweets" in name:
            return "pastry shop interior"
        if "pizza" in name or "burger" in name:
            return "modern fast food restaurant interior"
        
        # Priority 2: Cuisine based
        if "south indian" in cuisine:
            return "traditional south indian restaurant"
        if "chinese" in cuisine or "tibetan" in cuisine:
            return "oriental restaurant interior"
        if "fine dining" in cuisine or "continental" in cuisine:
            return "luxurious restaurant dining room"
        if "punjabi" in cuisine or "north indian" in cuisine:
            return "north indian restaurant interior"
        
        # Priority 3: General realistic restaurant interior
        return "premium restaurant interior landscape"

    def fetch_unique_image(self, query, index=0):
        """Fetch a unique image from Pexels."""
        if not self.api_key:
            return None
            
        params = {
            'query': query,
            'per_page': 1,
            'page': index + 1,  # Use page index for uniqueness
            'orientation': 'landscape'
        }
        
        try:
            response = requests.get(self.search_url, headers=self.headers, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get('photos'):
                    return data['photos'][0]['src']['large2x']
            else:
                print(f"  [!] Pexels Error ({response.status_code}): {response.text}")
        except Exception as e:
            print(f"  [!] Request Error: {e}")
        return None

    def download_image(self, url, restaurant_id):
        """Download and return ContentFile."""
        try:
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                ext = url.split('.')[-1].split('?')[0]
                if len(ext) > 4: ext = 'jpg'
                filename = f"res_{restaurant_id}_{uuid.uuid4().hex[:6]}.{ext}"
                return ContentFile(response.content, name=filename)
        except Exception as e:
            print(f"  [!] Download Error: {e}")
        return None

    def run(self, force=False):
        restaurants = Restaurant.objects.all().order_by('id')
        total = restaurants.count()
        print(f"Starting update for {total} restaurants...\n")

        success_count = 0
        for i, res in enumerate(restaurants):
            print(f"[{i+1}/{total}] Processing: {res.name}")
            
            # Skip if already has a realistic-looking custom image (heuristic: check if it's in the default list)
            # Actually, user wants to fix repetition, so we should probably update most of them if they are repeating.
            # For now, let's update all to ensure uniqueness if not specifically excluded.
            
            query = self.get_search_query(res)
            print(f"  -> Query: \"{query}\" (index {i})")
            
            img_url = self.fetch_unique_image(query, index=i)
            if img_url:
                img_content = self.download_image(img_url, res.id)
                if img_content:
                    res.cover_image.save(img_content.name, img_content, save=True)
                    print(f"  [OK] Assigned unique cover: {img_content.name}")
                    success_count += 1
                else:
                    print(f"  [X] Failed to download image")
            else:
                print(f"  [X] No image found on Pexels")
            
            # Rate limiting
            time.sleep(1.5)

        print(f"\nDone! Updated {success_count}/{total} restaurants.")

if __name__ == "__main__":
    updater = RestaurantCoverUpdater()
    updater.run()
