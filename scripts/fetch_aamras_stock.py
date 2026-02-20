import os
import sys
import django
from django.conf import settings

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import MenuItem
from ai_engine.stock_image_fetcher import StockImageFetcher

def fetch_aamras():
    try:
        # specific dish
        dish = MenuItem.objects.filter(name__iexact="Aamras (Seasonal)").first()
        
        if not dish:
            print("Error: Dish 'Aamras (Seasonal)' not found.")
            return

        print(f"Found dish: {dish.name} (ID: {dish.id})")
        
        fetcher = StockImageFetcher()
        if not fetcher.pexels_api_key:
            print("Error: PEXELS_API_KEY is not set.")
            return

        print("Attempting to fetch stock image...")
        result = fetcher.process_single(dish.id)
        
        if result['success']:
            print("Success! Image attached.")
            # Refresh to get URL
            dish.refresh_from_db()
            print(f"Image URL: {dish.image.url}")
        else:
            print(f"Failed: {result['message']}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    fetch_aamras()
