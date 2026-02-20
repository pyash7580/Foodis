import os
import django
import random
import uuid
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import User
from client.models import Restaurant, MenuItem, Order, OrderItem, Review, Category
from restaurant.models import RestaurantEarnings
from rider_legacy.models import RiderProfile, RiderEarnings, RiderReview

def populate_real_reviews():
    # 1. Get the main users
    admin_user = User.objects.filter(phone='9824948665').first()
    if not admin_user:
        print("Admin User 9824948665 not found!")
        return
    
    # Ensure we have a rider
    rider_user = User.objects.filter(role='RIDER').first()
    if not rider_user:
        rider_user = User.objects.create(
            phone="8888888888", 
            name="Rider Rahul", 
            role='RIDER',
            username="rider_rahul"
        )
        print(f"Created new rider: {rider_user.name}")
    
    rider_profile, _ = RiderProfile.objects.get_or_create(
        rider=rider_user,
        defaults={
            'vehicle_type': 'BIKE',
            'vehicle_number': 'GJ01AB1234',
            'license_number': 'GJ01202300001234',
            'status': 'APPROVED',
            'is_online': True
        }
    )

    restaurant = Restaurant.objects.filter(owner=admin_user).first()
    if not restaurant:
        print("No restaurant found for admin. Run populate_ai_test_data first.")
        return

    # 2. Get existing orders or create new ones
    orders = Order.objects.filter(restaurant=restaurant)
    if not orders.exists():
        print("No orders found. Please run populate_ai_test_data.py first.")
        return

    print(f"Adding real reviews to {orders.count()} orders...")
    
    restaurant_comments = [
        "Delicious food, highly recommended!",
        "The butter chicken was amazing, so creamy.",
        "On time delivery and hot food.",
        "Very good portion size and taste.",
        "Best biryani in the city.",
        "A bit spicy but very flavorful.",
        "Packaging was neat and clean.",
        "Authentic taste, will order again.",
        "Value for money.",
        "Great quality ingredients used."
    ]
    
    rider_comments = [
        "Very polite rider, delivered quickly.",
        "Smooth delivery experience.",
        "The rider followed my instructions perfectly.",
        "On time and professional.",
        "Friendly person, reached on time.",
        "Fastest delivery ever!",
        "Careful handling of the food package.",
        "Rider was helpful and patient with directions.",
        "Great service by the delivery partner.",
        "Punctual and efficient delivery."
    ]

    for order in orders:
        # Assign rider to order if not already assigned
        if not order.rider:
            order.rider = rider_user
            order.save()

        # Create/Update Restaurant Review
        res_rating = random.randint(3, 5)
        Review.objects.update_or_create(
            order=order,
            defaults={
                'user': order.user,
                'restaurant': restaurant,
                'rating': res_rating,
                'comment': random.choice(restaurant_comments)
            }
        )
        
        # Create/Update Rider Review (Independent of Restaurant Rating)
        rider_rating = random.randint(4, 5) # Generally riders get higher ratings if food is okay
        RiderReview.objects.update_or_create(
            order=order,
            defaults={
                'user': order.user,
                'rider': rider_user,
                'rating': rider_rating,
                'comment': random.choice(rider_comments)
            }
        )

    # Sync aggregates
    avg_res = Review.objects.filter(restaurant=restaurant).aggregate(Avg('rating'))['rating__avg'] or 4.0
    restaurant.rating = Decimal(str(round(float(avg_res), 2)))
    restaurant.save()
    
    avg_rider = RiderReview.objects.filter(rider=rider_user).aggregate(Avg('rating'))['rating__avg'] or 4.0
    rider_profile.rating = Decimal(str(round(float(avg_rider), 2)))
    rider_profile.save()

    print(f"Successfully added {orders.count()} independent reviews for Restaurant ({restaurant.rating}⭐) and Rider ({rider_profile.rating}⭐).")

if __name__ == "__main__":
    from django.db.models import Avg
    populate_real_reviews()
