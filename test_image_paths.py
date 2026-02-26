#!/usr/bin/env python
"""Test script to verify image paths are returned as relative /media/ paths"""

import requests
import json

# Test against local backend
API_URL = "http://127.0.0.1:8000"

def test_restaurant_images():
    """Test that restaurants return relative image paths"""
    try:
        print("\n=== Testing Restaurant Image Paths ===")
        res = requests.get(f"{API_URL}/api/client/restaurants/", headers={'X-Role': 'CLIENT'})
        
        if res.status_code != 200:
            print(f"[FAIL] Failed to fetch restaurants: {res.status_code}")
            return False
        
        data = res.json()
        # Handle both paginated and direct list responses
        if isinstance(data, dict):
            restaurants = data.get('results', [])
        else:
            restaurants = data if isinstance(data, list) else []
        
        if not restaurants:
            print("[SKIP] No restaurants found")
            return True
        
        restaurant = restaurants[0]
        print(f"\n[INFO] Testing restaurant: {restaurant.get('name')} (ID: {restaurant.get('id')})")
        
        # Check image_url
        if 'image_url' in restaurant:
            img_url = restaurant['image_url']
            if img_url:
                if img_url.startswith('/media/'):
                    print(f"[PASS] image_url is relative path: {img_url}")
                elif img_url.startswith('http://') or img_url.startswith('https://'):
                    print(f"[WARN] image_url is absolute URL: {img_url}")
                else:
                    print(f"[FAIL] image_url has unexpected format: {img_url}")
            else:
                print(f"[INFO] image_url is empty")
        
        # Check cover_image_url
        if 'cover_image_url' in restaurant:
            cover_url = restaurant['cover_image_url']
            if cover_url:
                if cover_url.startswith('/media/'):
                    print(f"[PASS] cover_image_url is relative path: {cover_url}")
                elif cover_url.startswith('http://') or cover_url.startswith('https://'):
                    print(f"[WARN] cover_image_url is absolute URL: {cover_url}")
                else:
                    print(f"[INFO] cover_image_url has fallback format (Unsplash)")
            else:
                print(f"[INFO] cover_image_url is empty")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_menu_items():
    """Test that menu items return relative image paths"""
    try:
        print("\n=== Testing Menu Item Image Paths ===")
        res = requests.get(f"{API_URL}/api/client/menu-items/", headers={'X-Role': 'CLIENT'})
        
        if res.status_code != 200:
            print(f"[FAIL] Failed to fetch menu items: {res.status_code}")
            return False
        
        data = res.json()
        # Handle both paginated and direct list responses
        if isinstance(data, dict):
            items = data.get('results', [])
        else:
            items = data if isinstance(data, list) else []
        
        if not items:
            print("[SKIP] No menu items found")
            return True
        
        item = items[0]
        print(f"\n[INFO] Testing menu item: {item.get('name')} (ID: {item.get('id')})")
        
        # Check image_url
        if 'image_url' in item:
            img_url = item['image_url']
            if img_url:
                if img_url.startswith('/media/'):
                    print(f"[PASS] image_url is relative path: {img_url}")
                elif img_url.startswith('http://') or img_url.startswith('https://'):
                    print(f"[WARN] image_url is absolute URL: {img_url}")
                else:
                    print(f"[FAIL] image_url has unexpected format: {img_url}")
            else:
                print(f"[INFO] image_url is empty")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("Testing Image Path Format")
    print("=" * 50)
    
    # First, try to connect to the backend
    try:
        res = requests.get(f"{API_URL}/api/health/", timeout=5)
        print(f"[OK] Backend is running at {API_URL}")
    except Exception as e:
        print(f"[ERROR] Cannot connect to backend at {API_URL}")
        print(f"Details: {e}")
        print("\nPlease make sure Django backend is running:")
        print("  python manage.py runserver")
        return
    
    # Run tests
    results = []
    results.append(("Restaurant Images", test_restaurant_images()))
    results.append(("Menu Item Images", test_menu_items()))
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")

if __name__ == '__main__':
    main()
