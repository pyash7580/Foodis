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

def populate_perfect_ai_data():
    print("🚀 Populating 'Perfect' AI Data for demonstration...")
    
    # 1. Get the main admin user
    user = User.objects.filter(phone='9824948665').first()
    if not user:
        print("User 9824948665 not found!")
        return
    
    restaurant = Restaurant.objects.filter(owner=user).first()
    if not restaurant:
        print("No restaurant found for 9824948665. Please create one.")
        return

    # 2. Setup Menu Items if they don't exist
    category, _ = Category.objects.get_or_create(name="Multicuisine", defaults={"slug": "multicuisine"})
    items = MenuItem.objects.filter(restaurant=restaurant)
    if not items.exists():
        menu_items_data = [
            ("Premium Butter Chicken", 350.00),
            ("Garlic Naan", 50.00),
            ("Veg Biryani", 220.00),
            ("Paneer Tikka", 280.00),
            ("Gulab Jamun", 80.00)
        ]
        for name, price in menu_items_data:
            MenuItem.objects.create(
                restaurant=restaurant, name=name, price=Decimal(str(price)),
                category=category, is_available=True
            )
        items = MenuItem.objects.filter(restaurant=restaurant)

    # 3. Create 100+ Realistic Orders
    clients = list(User.objects.filter(role='CLIENT'))
    if not clients:
        c = User.objects.create(phone="9000000005", name="Demo Customer", role='CLIENT', username="customer_demo")
        clients = [c]

    now = timezone.now()
    order_count = 0
    
    # Generate 150 historical orders
    for i in range(150):
        days_ago = random.randint(0, 30)
        if random.random() > 0.4:
            hour = random.choice([12, 13, 19, 20, 21])
        else:
            hour = random.randint(10, 22)
            
        timestamp = now - timedelta(days=days_ago)
        timestamp = timestamp.replace(hour=hour, minute=random.randint(0, 59))
        
        client = random.choice(clients)
        
        order = Order.objects.create(
            user=client,
            restaurant=restaurant,
            status='DELIVERED',
            payment_method='RAZORPAY',
            payment_status='PAID',
            delivery_address="AI Tech Park, Zone 5",
            delivery_latitude=Decimal("23.0225"),
            delivery_longitude=Decimal("72.5714"),
            delivery_phone=client.phone,
            subtotal=Decimal("0.00"),
            total=Decimal("0.00"),
            delivery_fee=Decimal("40.00"),
            tax=Decimal("15.00"),
        )
        # Fix timestamps
        Order.objects.filter(id=order.id).update(placed_at=timestamp, delivered_at=timestamp + timedelta(minutes=30))
        
        # Add items
        subtotal = Decimal("0.00")
        fav_item = MenuItem.objects.filter(restaurant=restaurant, name="Premium Butter Chicken").first()
        
        for _ in range(random.randint(1, 4)):
            item = fav_item if random.random() > 0.6 else random.choice(items)
            qty = random.randint(1, 2)
            OrderItem.objects.create(
                order=order, menu_item=item, quantity=qty,
                price=item.price, subtotal=item.price * qty
            )
            subtotal += (item.price * qty)
        
        order.subtotal = subtotal
        order.total = subtotal + order.delivery_fee + order.tax
        order.save()
        
        # Earnings
        RestaurantEarnings.objects.create(
            restaurant=restaurant, order=order, date=timestamp.date(),
            order_total=order.total, commission=order.total * Decimal('0.15'),
            net_amount=order.total * Decimal('0.85')
        )
        
        # High Ratings for 98% Health
        Review.objects.update_or_create(
            order=order,
            defaults={
                'user': client, 'restaurant': restaurant,
                'rating': 5 if random.random() > 0.2 else 4,
                'comment': "Excellent quality!"
            }
        )
        order_count += 1

    # 4. Create "Active" Orders for Kitchen Load
    for _ in range(3):
        Order.objects.create(
            user=random.choice(clients), restaurant=restaurant,
            status='PREPARING', payment_status='PAID', 
            delivery_latitude=Decimal("23.0225"), delivery_longitude=Decimal("72.5714"),
            total=Decimal("500.00")
        )

    print(f"✅ Created {order_count} historical orders and 3 active orders.")
    print("✨ AI Smart Dashboard is now perfectly data-optimized.")

if __name__ == "__main__":
    populate_perfect_ai_data()
