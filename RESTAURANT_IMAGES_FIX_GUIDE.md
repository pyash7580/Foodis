# Restaurant Images Display Fix - Complete Guide

## Problem
**Restaurant images are returning NULL from the API on production**

This happens because:
1. Local database has image data (files in media folder)
2. Production database (Neon) is empty - no image data
3. Production Render server doesn't have uploaded image files

## Solution
Use **external Pexels image URLs** instead of trying to serve files from disk.

---

## Steps to Fix

### Step 1: Create Django Migration (ADD IMAGE_URL FIELD)

Run these commands:
```bash
# Generate migration for new image_url field in Restaurant model
python manage.py makemigrations

# Apply migration to database
python manage.py migrate
```

**What this does:**
- Adds `image_url` URLField to Restaurant model
- Allows storing external image URLs directly in database
- Works on both local and production databases

### Step 2: Populate Production Database with Restaurants + Images

```bash
python populate_production_with_images.py
```

**What this does:**
- Creates 10 restaurants (Saffron Lounge, Thali Treasures, Pizza Paradise, etc.)
- Assigns free Pexels image URLs to each restaurant
- Creates 3-4 menu items per restaurant
- Works on local AND production Render database

**Images used:**
- Free Pexels images (no copyright issues)
- Direct HTTP URLs that work globally
- Automatically display without needing files on server

### Step 3: Deploy Code Changes

Commit and push these files:
```bash
git add -A
git commit -m "fix: Add image_url field and populate production database with restaurant images"
git push
```

**Files changed:**
- `client/models.py` - Added image_url field to Restaurant model
- `client/serializers.py` - Added image_url to RestaurantSerializer fields
- `frontend/src/components/RestaurantCard.js` - Updated to use image_url
- `populate_production_with_images.py` - New script to seed data

---

## What Happens After Fix

### Frontend displays images like this:
```
Restaurant card
├─ Check for image_url (external Pexels URL)
├─ If not, check cover_image (local file)
├─ If not, check image (local file)
└─ If none, show 🍽️ emoji fallback
```

### API Response Example:
```json
{
  "id": 1,
  "name": "Saffron Lounge",
  "image_url": "https://images.pexels.com/photos/... (external URL)",
  "cover_image": null,
  "image": null,
  "rating": 4.5,
  // ... other fields
}
```

---

## How to Test

### 1. Local Testing
```bash
# Run script to populate local database
python populate_production_with_images.py

# Start server
python manage.py runserver

# Visit http://localhost:3000/client
# Should see 10 restaurants with images
```

### 2. Production Testing
```bash
# After deploying to Render:

# 1. Run migrations on production database
# (Render will automatically run migrations from Procfile)

# 2. Run population script on production
# Option A: Use Render dashboard → Shell → Run script
# Option B: SSH into Render and run script

# 3. Visit your production site
# Should see restaurants with Pexels images
```

### 3. Browser DevTools Check
Open DevTools → Network tab:
- **Images tab**: Should see Pexels URLs loading with ✓ 200 status
- **Console**: No errors about 404 images
- **Application**: Check response from `/api/client/restaurants/`

---

## Image URLs Used

All restaurants use free Pexels URLs:
- https://images.pexels.com/photos/1410235/...  (Saffron Lounge - Indian food)
- https://images.pexels.com/photos/825661/...   (Pizza Paradise - Pizza)
- https://images.pexels.com/photos/1092730/... (Thali Treasures - Food plate)
- And 7 more...

**Why Pexels?**
- ✓ Free, public, no copyright
- ✓ No authentication needed
- ✓ Works globally
- ✓ Fast CDN delivery
- ✓ No expiration

---

## Troubleshooting

### Images still showing as NULL after running script?
```bash
# Check if script created restaurants
python manage.py shell
>>> from client.models import Restaurant
>>> Restaurant.objects.count()
10  # Should show 10

# Check if image_url is populated
>>> r = Restaurant.objects.first()
>>> r.image_url
'https://images.pexels.com/...'  # Should show URL
```

### Images showing broken on frontend?
1. Check API response:
   ```bash
   curl http://localhost:8000/api/client/restaurants/
   # Look for "image_url" field with https://... value
   ```

2. Check frontend prioritization:
   - `RestaurantCard.js` should prefer `image_url`
   - Falls back to `cover_image`, then `image`

### Pexels URLs not loading?
- Check browser console for CORS errors
- Pexels allows CORS by default, should work
- Check network tab - Pexels server must respond with 200

---

## Future Enhancements

### 1. Allow Restaurants to Upload Images
Modify `populate_production_with_images.py` to:
- Keep external URLs as fallback
- Allow restaurants to upload their own images
- Store via ImageField (local files on production)

### 2. Image Optimization
- Add Pillow to generate thumbnails
- Serve WebP format for better compression
- Use Cloudinary for CDN delivery

### 3. Local Image Upload
- For restaurants that upload images:
  - Store in media/restaurants/ folder
  - Use `cover_image` field (ImageField)
  - Allows both local and external URLs

---

## Summary of Changes

| File | Change | Impact |
|------|--------|--------|
| `client/models.py` | Added `image_url` field | Store external URLs |
| `client/serializers.py` | Added `image_url` field | Return URLs in API |
| `RestaurantCard.js` | Check `image_url` first | Display images |
| `populate_production_with_images.py` | New script | Seed 10 restaurants |
| `foodis/urls.py` | Media serving fix | Serve /media/ files |

---

## Questions?

If images still don't show:
1. Check API response has `image_url` with https:// URL
2. Check frontend uses that URL for backgroundImage
3. Check network tab - is Pexels URL loading?
4. Check console for JavaScript errors

All issues should be resolved by following these steps!
