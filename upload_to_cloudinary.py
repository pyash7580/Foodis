import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

import cloudinary.uploader
from restaurant.models import Restaurant
from django.conf import settings

MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT',
                     os.path.join(settings.BASE_DIR, 'media'))

restaurants = Restaurant.objects.all()
success = 0

for r in restaurants:
    try:
        # Get local image path
        img_field = getattr(r, 'image', None) or getattr(r, 'image_url', None)
        if not img_field:
            continue
        
        img_str = str(img_field)
        if img_str.startswith('http'):
            print(f"⏭️  Already URL: {r.name}")
            continue
        
        # Build full local path
        if img_str.startswith('/media/'):
            local_path = os.path.join(settings.BASE_DIR, img_str.lstrip('/'))
        else:
            local_path = os.path.join(MEDIA_ROOT, img_str)
        
        if not os.path.exists(local_path):
            print(f"⚠️  File not found: {r.name} — {local_path}")
            continue
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            local_path,
            folder='foodis/restaurants',
            public_id=f'restaurant_{r.pk}',
            overwrite=True,
            resource_type='image'
        )
        
        cloud_url = result['secure_url']
        
        # Save Cloudinary URL back to restaurant
        if hasattr(r, 'image_url'):
            r.image_url = cloud_url
            r.save(update_fields=['image_url'])
        elif hasattr(r, 'image'):
            r.image = cloud_url
            r.save(update_fields=['image'])
        
        print(f"✅ {r.name} → {cloud_url}")
        success += 1
    
    except Exception as e:
        print(f"❌ {r.name}: {e}")

print(f"\n✅ Uploaded {success} images to Cloudinary")
