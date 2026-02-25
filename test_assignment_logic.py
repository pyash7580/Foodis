import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from rider_legacy.models import RiderProfile
from client.models import Order
from core.models import City
from django.db.models import Q
from geopy.distance import distance

def test_logic():
    print("Testing Rider Assignment Logic...")
    
    # Let's find a rider profile that has a city set
    profile = RiderProfile.objects.exclude(city='').first()
    if not profile:
        print("No rider profiles found. Creating one...")
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.filter(role='RIDER').first()
        city = City.objects.first()
        profile = RiderProfile.objects.create(rider=user, city=city.name, city_id=city, status='APPROVED', is_online=True, current_latitude=23.5880, current_longitude=72.3693)
    else:
        profile.status = 'APPROVED'
        profile.is_online = True
        profile.current_latitude = 23.5880 
        profile.current_longitude = 72.3693
        profile.save()

    print(f"Using Rider: {profile.rider.phone}, City: {profile.city}, CityID: {profile.city_id}")

    # Ensure there are some test orders in the same city
    print("Checking orders...")
    restaurant = profile.city_id.restaurants.first() if profile.city_id else None
    if restaurant:
        Order.objects.filter(restaurant=restaurant).update(status='READY', rider=None)
        
    city_filters = Q()
    if profile.city_id:
        city_filters |= Q(city_id=profile.city_id)
        city_filters |= Q(restaurant__city_id=profile.city_id)
        
    if profile.city:
        city_filters |= Q(restaurant__city__iexact=profile.city)

    print("City Filters:", city_filters)
    
    available_orders = Order.objects.filter(
        city_filters,
        status__in=['CONFIRMED', 'PREPARING', 'READY'],
        rider__isnull=True
    ).select_related('restaurant')
    
    print(f"Found {available_orders.count()} matching orders.")
    
    rider_location = (float(profile.current_latitude), float(profile.current_longitude))
    
    for order in available_orders[:3]:
        print(f" - Order {order.id} | City ID: {order.city_id_id} | Rest City: {order.restaurant.city}")
        restaurant_location = (float(order.restaurant.latitude), float(order.restaurant.longitude))
        dist = distance(rider_location, restaurant_location).km
        print(f"   Dist: {dist:.2f} km")

if __name__ == '__main__':
    test_logic()
