import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.contrib.auth import get_user_model
from client.models import Restaurant, Order, Review

User = get_user_model()

def seed_reviews():
    print("--- Seeding Reviews ---")
    
    users = list(User.objects.filter(role='CLIENT'))
    restaurants = list(Restaurant.objects.filter(status='APPROVED'))
    
    if not users or not restaurants:
        print("Not enough users or restaurants to seed reviews.")
        return

    count = 0
    for _ in range(20):
        user = random.choice(users)
        restaurant = random.choice(restaurants)
        
        # Find a delivered order for this user/restaurant pair if possible, else create independent review
        # The model allows null order, but unique_together is ['user', 'order']. 
        # Actually unique_together is user, order. If order is null, can we have multiple reviews? 
        # Django docs say unique_together with null is tricky. 
        # Let's try to link to an order if possible.
        
        order = Order.objects.filter(user=user, restaurant=restaurant, status='DELIVERED').first()
        
        try:
            review = Review.objects.create(
                user=user,
                restaurant=restaurant,
                order=order,
                rating=random.randint(1, 5),
                comment=random.choice([
                    "Great food!", "Delivery was slow.", "Loved the taste.", 
                    "Packaging could be better.", "Excellent service!", 
                    "Not bad, but expensive.", "Will order again."
                ])
            )
            count += 1
            print(f"Created review for {restaurant.name} by {user.name}")
        except Exception as e:
            # Likely unique constraint or something
            pass
            
    print(f"Seeded {count} reviews.")

if __name__ == '__main__':
    seed_reviews()
