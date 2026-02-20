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
            name="AI Smart Kitchen",
            slug=f"ai-smart-kitchen-{uuid.uuid4().hex[:4]}",
            phone="9998887776",
            address="Test Street, AI Block",
            city="Ahmedabad",
            state="Gujarat",
            pincode="380001",
            latitude=Decimal("23.0225"),
            longitude=Decimal("72.5714"),
            status='APPROVED',
            is_active=True,
            rating=Decimal("4.5")
        )
        print(f"Created new restaurant: {restaurant.name}")
    else:
        # Update existing to be approved for testing
        restaurant.status = 'APPROVED'
        restaurant.is_active = True
        restaurant.save()
        print(f"Found and updated restaurant: {restaurant.name}")

    # 2. Ensure we have categories
    category, _ = Category.objects.get_or_create(name="Multicuisine", defaults={"slug": "multicuisine"})

    # 3. Ensure we have menu items
    items = MenuItem.objects.filter(restaurant=restaurant)
    if not items.exists():
        menu_items_data = [
            ("Premium Butter Chicken", 350.00, "Signature dish"),
            ("Garlic Naan", 50.00, "Freshly baked"),
            ("Veg Biryani", 220.00, "Aromatic rice"),
            ("Cold Coffee", 120.00, "Refreshing"),
            ("Paneer Tikka", 280.00, "Grilled perfection"),
            ("Gulab Jamun", 80.00, "Sweet dessert")
        ]
        for name, price, desc in menu_items_data:
            MenuItem.objects.create(
                restaurant=restaurant,
                name=name,
                price=Decimal(str(price)),
                description=desc,
                category=category,
                is_available=True
            )
        items = MenuItem.objects.filter(restaurant=restaurant)
        print(f"Created {items.count()} menu items")

    # 4. Create realistic orders for the last 30 days
    print("Generating 50+ realistic orders...")
    clients = User.objects.filter(role='CLIENT')
    if not clients.exists():
        # Create a test client if none exist
        c = User.objects.create(phone="9000000001", name="Test Customer", role='CLIENT', username="client1")
        clients = User.objects.filter(id=c.id)

    now = timezone.now()
    order_count = 0
    
    for i in range(60):
        days_ago = random.randint(0, 30)
        hour = random.choice([11, 12, 13, 14, 18, 19, 20, 21, 22])
        timestamp = now - timedelta(days=days_ago)
        timestamp = timestamp.replace(hour=hour, minute=random.randint(0, 59))
        
        client = random.choice(list(clients))
        
        order = Order(
            user=client,
            restaurant=restaurant,
            status='DELIVERED',
            payment_method='RAZORPAY',
            payment_status='PAID',
            delivery_address="123 AI Test Resident",
            delivery_latitude=Decimal("23.0225"),
            delivery_longitude=Decimal("72.5714"),
            delivery_phone=client.phone,
            subtotal=Decimal("100.00"), # temporary
            total=Decimal("155.00"),    # temporary
            delivery_fee=Decimal("40.00"),
            tax=Decimal("15.00"),
        )
        order.save()
        
        # Override timestamps
        Order.objects.filter(id=order.id).update(
            placed_at=timestamp,
            delivered_at=timestamp + timedelta(minutes=random.randint(30, 50))
        )
        order.refresh_from_db()

        # Add items
        subtotal = Decimal("0.00")
        for _ in range(random.randint(1, 4)):
            item = random.choice(list(items))
            qty = random.randint(1, 2)
            OrderItem.objects.create(
                order=order,
                menu_item=item,
                quantity=qty,
                price=item.price,
                subtotal=item.price * Decimal(str(qty))
            )
            subtotal += (item.price * Decimal(str(qty)))
        
        order.subtotal = subtotal
        order.total = subtotal + order.delivery_fee + order.tax
        order.save()
        
        # Create earnings entry
        RestaurantEarnings.objects.create(
            restaurant=restaurant,
            order=order,
            date=timestamp.date(),
            order_total=order.total,
            commission=order.total * Decimal('0.15'),
            net_amount=order.total * Decimal('0.85')
        )
        
        # Add reviews
        if random.random() > 0.6:
            Review.objects.update_or_create(
                user=client,
                order=order,
                defaults={
                    'restaurant': restaurant,
                    'rating': random.randint(3, 5),
                    'comment': random.choice(["Excellent food!", "Loved it", "Great AI service", "Yummy!", "Good quality"])
                }
            )
            
        order_count += 1

    print(f"Successfully populated {order_count} orders for AI evaluation for restaurant: {restaurant.name}")

if __name__ == "__main__":
    populate_ai_data()
