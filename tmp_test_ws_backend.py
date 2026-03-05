import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import User
from rider_legacy.models import RiderProfile
from core.city_utils import normalize_city_name

try:
    user_id = 508
    print(f"Testing for user ID {user_id}")
    rider = RiderProfile.objects.get(rider_id=user_id)
    print(f"Found Rider Profile: {rider}")
    
    if rider.city:
        normalized_city = normalize_city_name(rider.city)
        print(f"Normalized city: {normalized_city}")
    else:
        print("No city found on rider")

except Exception as e:
    import traceback
    traceback.print_exc()

# Also let's check what the nearby orders logic shows for 508
from client.models import Order
from django.db.models import Q
from geopy.distance import distance

profile = RiderProfile.objects.filter(rider_id=508).first()
if not profile:
    print("No profile for 508")
    exit()

if profile.is_online == False:
    profile.is_online = True
    profile.save()

city_filters = Q()
if profile.city_id:
    city_filters |= Q(city_id=profile.city_id)
    city_filters |= Q(restaurant__city_id=profile.city_id)

if profile.city:
    city_filters |= Q(restaurant__city__iexact=profile.city)

available_orders = Order.objects.filter(
    city_filters,
    status__in=['CONFIRMED', 'PREPARING', 'READY'],
    rider__isnull=True
).select_related('restaurant')

print(f"Orders passing city filters for 508: {available_orders.count()}")

nearby_orders = []
rider_location = None
if profile.current_latitude and profile.current_longitude:
    rider_location = (float(profile.current_latitude), float(profile.current_longitude))

for order in available_orders:
    dist = None
    if rider_location and order.restaurant.latitude and order.restaurant.longitude:
        try:
            restaurant_location = (float(order.restaurant.latitude), float(order.restaurant.longitude))
            dist = distance(rider_location, restaurant_location).km
            print(f"Order #{order.id} - Dist: {dist} km")
        except Exception as e:
            print(f"Error calcing dist: {e}")
        
        if dist is not None and dist > 20:
            print(f"Filtered out! {dist} > 20km")
            continue
    else:
        print(f"Order #{order.id} missing location")
    
    nearby_orders.append(order.id)

print(f"Final Nearby Orders IDs for 508: {nearby_orders}")
