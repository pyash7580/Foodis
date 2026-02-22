import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import Restaurant

# Free permanent food images from Unsplash (no key needed)
FOOD_IMAGES = [
    'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800',
    'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800',
    'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800',
    'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800',
    'https://images.unsplash.com/photo-1552566626-52f8b828add9?w=800',
    'https://images.unsplash.com/photo-1537047902294-62a40c20a6ae?w=800',
    'https://images.unsplash.com/photo-1424847651672-bf20a4b0982b?w=800',
    'https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?w=800',
    'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800',
    'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800',
    'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800',
    'https://images.unsplash.com/photo-1473093295043-cdd812d0e601?w=800',
    'https://images.unsplash.com/photo-1498654896293-37aacf113fd9?w=800',
    'https://images.unsplash.com/photo-1544025162-d76694265947?w=800',
    'https://images.unsplash.com/photo-1482049016688-2d3e1b311543?w=800',
    'https://images.unsplash.com/photo-1559847844-5315695dadae?w=800',
]

restaurants = Restaurant.objects.all()
updated = 0

for i, restaurant in enumerate(restaurants):
    try:
        # Assign image URL cycling through our list
        image_url = FOOD_IMAGES[i % len(FOOD_IMAGES)]
        
        # Check which field the model uses
        if hasattr(restaurant, 'image_url'):
            restaurant.image_url = image_url
        elif hasattr(restaurant, 'image'):
            # If image is a URLField or CharField store directly
            # If ImageField, we store the URL string
            restaurant.image = image_url
        
        # Also set is_active and is_approved
        restaurant.is_active = True
        restaurant.status = 'APPROVED' # Based on my exploration, status field is used for approval
        restaurant.save()
        print(f"✅ {restaurant.name} → image assigned")
        updated += 1
    except Exception as e:
        print(f"❌ {restaurant.name} → {e}")

print(f"\n✅ Done: {updated}/{restaurants.count()} restaurants updated")
