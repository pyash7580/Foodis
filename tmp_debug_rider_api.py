import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import User
from client.models import Order
from rider_legacy.models import RiderProfile
from geopy.distance import distance
from django.db.models import Q

with open('debug_orders_8.txt', 'w') as f:
    try:
        user = User.objects.get(id=8)
        profile = RiderProfile.objects.filter(rider=user).first()
        
        if not profile:
            f.write("Profile doesn't exist.\n")
            exit()
            
        if not profile.is_online:
            f.write("Profile is offline. Forcing online for test...\n")
            profile.is_online = True
            profile.save()

        f.write(f"Rider Profile: {profile.rider.name}, City: {profile.city}\n")
        f.write(f"Rider Location: lat={profile.current_latitude}, lng={profile.current_longitude}\n")

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

        f.write(f"Orders passing city filters: {available_orders.count()}\n")

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
                    f.write(f"Order #{order.id} - Dist: {dist} km\n")
                except Exception as e:
                    f.write(f"Error calcing dist: {e}\n")
                
                if dist is not None and dist > 20:
                    f.write(f"Filtered out! {dist} > 20km\n")
                    continue
            else:
                f.write(f"Order #{order.id} missing location (Rider loc: {rider_location}, Rest loc: {order.restaurant.latitude}, {order.restaurant.longitude})\n")
            
            nearby_orders.append(order.id)

        f.write(f"Final Nearby Orders IDs: {nearby_orders}\n")
        
    except Exception as e:
        f.write(f"Exception: {e}\n")
