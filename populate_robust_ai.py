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

def create_demo_order(user, restaurant, items, date, status='DELIVERED'):
    order_id = f"ORD{uuid.uuid4().hex[:8].upper()}"
    
    order = Order.objects.create(
        order_id=order_id,
        user=user,
        restaurant=restaurant,
        status=status,
        payment_method='RAZORPAY',
        payment_status='PAID',
        delivery_address="AI Tech Park, Zone 5, Ahmedabad",
        delivery_latitude=Decimal("23.0225"),
        delivery_longitude=Decimal("72.5714"),
        delivery_phone=user.phone,
        subtotal=Decimal("0.00"),
        total=Decimal("0.00"),
        delivery_fee=Decimal("40.00"),
        tax=Decimal("15.00"),
    )
    
    # Manual update for historical tracking
    Order.objects.filter(id=order.id).update(
        placed_at=date,
        delivered_at=date + timedelta(minutes=random.randint(25, 45)) if status == 'DELIVERED' else None
    )
    
    # Add items
    subtotal = Decimal("0.00")
    for _ in range(random.randint(1, 3)):
        item = random.choice(items)
        qty = random.randint(1, 2)
        OrderItem.objects.create(
            order=order, menu_item=item, quantity=qty,
            price=item.price, subtotal=item.price * qty
        )
        subtotal += (item.price * qty)
    
    order.subtotal = subtotal
    order.total = subtotal + order.delivery_fee + order.tax
    order.save()
    
    if status == 'DELIVERED':
        RestaurantEarnings.objects.create(
            restaurant=restaurant, order=order, date=date.date(),
            order_total=order.total, commission=order.total * Decimal('0.15'),
            net_amount=order.total * Decimal('0.85')
        )
        # Random high rating
        Review.objects.update_or_create(
            order=order,
            defaults={
                'user': user, 'restaurant': restaurant,
                'rating': random.choice([4, 5, 5]),
                'comment': "Amazing Food! AI-recommended."
            }
        )
    return order

def populate_robust_data():
    print("🚀 Running Robust AI Data Population...")
    admin = User.objects.filter(phone='9824948665').first()
    restaurant = Restaurant.objects.filter(owner=admin).first()
    
    if not restaurant:
        print("Restaurant not found.")
        return

    # Categories and Menu
    cat, _ = Category.objects.get_or_create(name="Italian", defaults={"slug": "italian"})
    menu_data = [
        ("Truffle Pizza", 499), ("Pesto Pasta", 350), ("Lasagna", 420),
        ("Tiramisu", 280), ("Espresso", 120), ("Bruschetta", 220)
    ]
    for name, p in menu_data:
        MenuItem.objects.get_or_create(
            restaurant=restaurant, name=name,
            defaults={'price': Decimal(str(p)), 'category': cat, 'is_available': True}
        )
    
    items = list(MenuItem.objects.filter(restaurant=restaurant))
    clients = list(User.objects.filter(role='CLIENT'))
    if not clients:
        clients = [admin]

    now = timezone.now()
    
    # 1. Historical Data (120 orders)
    print("Generating historical orders...")
    for i in range(120):
        days_ago = random.randint(0, 28)
        # Peak Hours logic: Lunch 12-2, Dinner 7-9
        if random.random() > 0.3:
            hour = random.choice([12, 13, 19, 20])
        else:
            hour = random.randint(10, 22)
            
        timestamp = now - timedelta(days=days_ago)
        timestamp = timestamp.replace(hour=hour, minute=random.randint(0, 59))
        create_demo_order(random.choice(clients), restaurant, items, timestamp)

    # 2. Kitchen Load (Active Orders)
    print("Creating active kitchen load...")
    for _ in range(6):
        create_demo_order(random.choice(clients), restaurant, items, now, status='PREPARING')

    print("✅ Robust Population Complete!")

if __name__ == "__main__":
    populate_robust_data()
