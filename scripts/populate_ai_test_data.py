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
from client.models import Restaurant, MenuItem, Order, OrderItem, Review
from restaurant.models import RestaurantEarnings

def populate_ai_data():
    # 1. Get the user and their restaurant
    user = User.objects.filter(phone='9824948665').first()
    if not user:
        print("User 9824948665 not found!")
        return
    
    restaurant = Restaurant.objects.filter(owner=user).first()
    if not restaurant:
        # If no restaurant, create one for testing
        restaurant = Restaurant.objects.create(
            owner=user,
            name="AI Test Kitchen",
            phone="9998887776",
            address="Test Street",
            city="Ahmedabad",
            cuisine_type="Multicuisine",
            status='APPROVED',
            is_active=True,
            rating=4.5
        )
        print(f"Created new restaurant: {restaurant.name}")
    else:
        print(f"Found restaurant: {restaurant.name}")

    # 2. Ensure we have menu items
    items = MenuItem.objects.filter(restaurant=restaurant)
    if not items.exists():
        menu_data = [
            ("Premium Butter Chicken", 350, "Signature dish"),
            ("Garlic Naan", 50, "Freshly baked"),
            ("Veg Biryani", 220, "Aromatic rice"),
            ("Cold Coffee", 120, "Refreshing"),
            ("Paneer Tikka", 280, "Grilled perfection")
        ]
        for name, price, desc in menu_data:
            MenuItem.objects.create(
                restaurant=restaurant,
                name=name,
                price=price,
                description=desc,
                category="Main Course",
                is_available=True
            )
        items = MenuItem.objects.filter(restaurant=restaurant)
        print(f"Created {items.count()} menu items")

    # 3. Create realistic orders for the last 30 days
    print("Generating 50+ realistic orders...")
    clients = User.objects.filter(role='CLIENT')[:10]
    if not clients:
        # Create a test client if none exist
        c = User.objects.create(phone="9000000001", name="Test Customer", role='CLIENT')
        clients = [c]

    now = timezone.now()
    order_count = 0
    
    for i in range(55):
        days_ago = random.randint(0, 30)
        hour = random.choice([12, 13, 14, 19, 20, 21, 22]) # Lunch and Dinner peaks
        placed_at = now - timedelta(days=days_ago)
        placed_at = placed_at.replace(hour=hour, minute=random.randint(0, 59))
        
        client = random.choice(clients)
        
        order = Order.objects.create(
            user=client,
            restaurant=restaurant,
            status='DELIVERED',
            payment_status='PAID',
            payment_method='UPI',
            total=0,
            delivery_address="Mock Address",
            placed_at=placed_at,
            delivered_at=placed_at + timedelta(minutes=random.randint(25, 45))
        )
        
        # Add random items
        total = 0
        for _ in range(random.randint(1, 4)):
            item = random.choice(items)
            qty = random.randint(1, 2)
            OrderItem.objects.create(
                order=order,
                menu_item=item,
                quantity=qty,
                price=item.price
            )
            total += (item.price * qty)
        
        order.total = total
        order.subtotal = total
        order.save()
        
        # Create earnings entry
        RestaurantEarnings.objects.create(
            restaurant=restaurant,
            order=order,
            date=placed_at.date(),
            total_amount=total,
            commission_amount=total * Decimal('0.1'),
            net_amount=total * Decimal('0.9'),
            status='PAID'
        )
        
        # Randomly add reviews
        if random.random() > 0.7:
            Review.objects.create(
                user=client,
                restaurant=restaurant,
                order=order,
                rating=random.randint(3, 5),
                comment="Great food!"
            )
            
        order_count += 1

    print(f"Successfully populated {order_count} orders for AI evaluation.")

if __name__ == "__main__":
    populate_ai_data()
