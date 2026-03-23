import os
import sys
import django


# Setup Django environment
sys.path.append(r'd:\Foodis')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.contrib.auth import get_user_model
from client.models import Restaurant, FavouriteRestaurant
from client.views import RestaurantListView, FavouriteRestaurantViewSet
from rest_framework.test import APIRequestFactory, force_authenticate

User = get_user_model()
factory = APIRequestFactory()

def test_favourites_api():
    # 1. Create/Get a user
    user, _ = User.objects.get_or_create(email='testuser_favs@example.com', defaults={'name': 'Test User'})
    
    # 2. Get any approved restaurant
    restaurant = Restaurant.objects.filter(status='APPROVED').first()
    if not restaurant:
        print("No approved restaurants found. Cannot test.")
        return
        
    print(f"Testing with Restaurant: {restaurant.name} (ID: {restaurant.id})")
    
    # 3. Add to favourites directly
    FavouriteRestaurant.objects.get_or_create(user=user, restaurant=restaurant)
    print("- Added to user's favourites in DB.")

    # 4. Test RestaurantListView includes `is_favourite=True`
    request = factory.get('/api/client/restaurants/')
    force_authenticate(request, user=user)
    view = RestaurantListView.as_view()
    response = view(request)
    
    data = response.data
    target_rest = next((r for r in data if r['id'] == restaurant.id), None)
    if not target_rest:
        print("x ERROR: Restaurant not found in list API response!")
    else:
        is_fav = target_rest.get('is_favourite')
        print(f"- Custom List API is_favourite: {is_fav} (Expected: True)")
        if is_fav is not True:
             print("x ERROR: is_favourite is not correctly populated in custom list view.")

    # 5. Test FavouriteRestaurantViewSet serializer outputs correct fields
    request2 = factory.get('/api/client/favourite-restaurants/')
    force_authenticate(request2, user=user)
    view2 = FavouriteRestaurantViewSet.as_view({'get': 'list'})
    response2 = view2(request2)
    
    fav_data = response2.data
    # Handling pagination or list
    items = fav_data.get('results') if isinstance(fav_data, dict) and 'results' in fav_data else fav_data
    
    rest_details = items[0]['restaurant_details'] if items else {}
    if rest_details:
        print("\nChecking FavouriteRestaurant API Serializer Details:")
        print(f"  image_url returns: {'YES' if 'image_url' in rest_details else 'NO'}")
        print(f"  city_name returns: {'YES' if 'city_name' in rest_details else 'NO'}")
        print(f"  image returns:     {'YES' if 'image' in rest_details else 'NO'} (Should be NO, validating our frontend fix)")
    else:
        print("x ERROR: Failed to get favourite restaurants from API.")
        
    print("\nLocal verification complete!")

if __name__ == '__main__':
    test_favourites_api()
