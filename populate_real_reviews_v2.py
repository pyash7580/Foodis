import os
import django
import random
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import User
from client.models import Restaurant, Order, Review, MenuItem, OrderItem
from rider_legacy.models import RiderProfile, RiderReview

def populate_all_reviews():
    print("🚀 Starting comprehensive review population...")
    
    # 1. Get all relevant users
    all_clients = list(User.objects.filter(role='CLIENT'))
    admin_user = User.objects.filter(phone='9824948665').first()
    if admin_user and admin_user not in all_clients:
        all_clients.append(admin_user)
    
    if not all_clients:
        print("No clients found. Creating a test client.")
        c = User.objects.create(phone="9000000002", name="Reviewer John", role='CLIENT', username="reviewer_john")
        all_clients = [c]

    # 2. Get all restaurants and riders
    all_restaurants = Restaurant.objects.filter(status='APPROVED')
    all_riders = RiderProfile.objects.filter(status='APPROVED')
    
    if not all_restaurants.exists():
        print("No approved restaurants found.")
        return

    # Comments for variety
    res_comments = [
        "Absolutely delicious! The flavors were perfectly balanced.",
        "Best meal I've had in ages. Highly recommend the chef's special.",
        "Good food, but the portion size was a bit small for the price.",
        "The packaging was excellent. Food arrived hot and fresh.",
        "A bit too spicy for my taste, but very authentic.",
        "Value for money. Great quality and quantity.",
        "My go-to place for weekend dinners. Never disappoints.",
        "The dessert was the highlight of the meal!",
        "Healthy and tasty. Perfect for a quick lunch.",
        "Decent food, but I've had better elsewhere."
    ]
    
    rider_comments = [
        "Super fast delivery! Rider was very professional.",
        "Polite and helpful rider. Reached my location easily.",
        "Great handling of the food. Nothing spilled.",
        "Delivered exactly on time. Impressed with the speed.",
        "Rider was very courteous and followed delivery notes.",
        "Prompt service. Much appreciated.",
        "The rider was patient even though my doorbell was broken.",
        "Professional and friendly. Five stars!",
        "Reached before the estimated time. Amazing!",
        "Good behavior and safe driving."
    ]

    review_count = 0
    
    for restaurant in all_restaurants:
        print(f"Processing restaurant: {restaurant.name}")
        
        # Ensure the restaurant has some historical orders
        orders = Order.objects.filter(restaurant=restaurant, status='DELIVERED')
        
        if not orders.exists():
            print(f"  No orders for {restaurant.name}, skipped reviews.")
            continue

        for order in orders:
            # Randomly decide if this order gets a review (80% chance for demo)
            if random.random() < 0.8:
                # Use the order's user if possible, otherwise a random client
                reviewer = order.user or random.choice(all_clients)
                
                # RESTAURANT REVIEW
                res_rating = random.randint(3, 5)
                # If it's a 3 star, maybe a slightly critical comment
                comment = random.choice(res_comments)
                
                Review.objects.update_or_create(
                    order=order,
                    defaults={
                        'user': reviewer,
                        'restaurant': restaurant,
                        'rating': res_rating,
                        'comment': comment
                    }
                )
                
                # RIDER REVIEW
                if order.rider:
                    rider_rating = random.randint(4, 5) # Riders usually get better ratings
                    RiderReview.objects.update_or_create(
                        order=order,
                        defaults={
                            'user': reviewer,
                            'rider': order.rider,
                            'rating': rider_rating,
                            'comment': random.choice(rider_comments)
                        }
                    )
                review_count += 1

    # 3. Final Step: Sync the aggregate ratings back to Profiles
    print("Syncing aggregate ratings...")
    for res in all_restaurants:
        avg = Review.objects.filter(restaurant=res).aggregate(Avg('rating'))['rating__avg']
        count = Review.objects.filter(restaurant=res).count()
        if avg:
            res.rating = Decimal(str(round(float(avg), 2)))
        res.total_ratings = count
        res.save()

    for rp in all_riders:
        avg = RiderReview.objects.filter(rider=rp.rider).aggregate(Avg('rating'))['rating__avg']
        if avg:
            rp.rating = Decimal(str(round(float(avg), 2)))
        rp.save()

    print(f"✅ Success! Created/Updated {review_count} comprehensive real reviews.")

if __name__ == "__main__":
    from django.db.models import Avg
    populate_all_reviews()
