import os
import django
import random
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import Order, User, Restaurant, Wallet, WalletTransaction
from rider_legacy.models import RiderProfile
from restaurant.models import RestaurantEarnings

def populate_analytics():
    print("Injecting AI Analytics Datasets...")
    
    # Needs:
    # 1. City Trends (Orders in distinct cities)
    # 2. Fraud (Cancellations, Wallet Spikes)
    # 3. Rider Efficiency (Varied delivery times)

    # --- 1. City Trends ---
    cities = ['Mumbai', 'Bangalore', 'Delhi', 'Chennai', 'Hyderabad']
    print(f"Distributing restaurants across {len(cities)} cities...")
    
    for i, city in enumerate(cities):
        # Create or update a restaurant in this city
        owner_email = f"owner_{city.lower()}@foodis.com"
        try:
            user = User.objects.get(email=owner_email)
            restaurant = user.restaurant
        except User.DoesNotExist:
            user = User.objects.create_user(
                phone=f'+9198{i}0000000',
                email=owner_email,
                name=f'{city} Bistro',
                role='RESTAURANT',
                password='password'
            )
            restaurant = Restaurant.objects.create(
                owner=user,
                name=f'{city} Spice Hub',
                slug=f'{city.lower()}-spice-hub',
                phone=f'98{i}0000000',
                address='123 Main St',
                city=city,
                state='State',
                pincode='100001',
                latitude=Decimal('12.0'),
                longitude=Decimal('77.0'),
                status='APPROVED',
                image='restaurants/default.jpg' 
            )
        
        # Create orders for this city
        print(f"  -> Generating orders for {city}...")
        client_user = User.objects.filter(role='CLIENT').first()
        if not client_user:
            client_user = User.objects.create_user(phone='+919999999999', name='Test Client', role='CLIENT')

        for _ in range(random.randint(5, 15)):
            Order.objects.create(
                user=client_user,
                restaurant=restaurant,
                total=Decimal(random.randint(300, 2000)),
                subtotal=Decimal('300.00'),
                status='DELIVERED',
                payment_status='PAID',
                payment_method='RAZORPAY',
                placed_at=timezone.now() - timedelta(days=random.randint(1, 25)),
                delivery_latitude=Decimal('0'), delivery_longitude=Decimal('0'), delivery_phone='000',
                delivery_address='Test Address'
            )

    # --- 2. Fraud Simulation ---
    print("Simulating Fraud Patterns...")
    
    # Case A: Serial Canceller
    fraud_user, _ = User.objects.get_or_create(
        phone='+919996669999',
        defaults={'name': 'Suspicious Sam', 'role': 'CLIENT'}
    )
    for _ in range(5):
        Order.objects.create(
            user=fraud_user,
            restaurant=Restaurant.objects.first(),
            total=Decimal('6500.00'), # High Value
            subtotal=Decimal('6500.00'),
            status='CANCELLED',
            payment_status='REFUNDED',
            payment_method='WALLET',
            placed_at=timezone.now(),
            delivery_latitude=Decimal('0'), delivery_longitude=Decimal('0'), delivery_phone='000',
            delivery_address='Test Address'
        )
        
    # Case B: Wallet Launderer
    launder_user, _ = User.objects.get_or_create(
        phone='+918887776666', 
        defaults={'name': 'Money Mike', 'role': 'CLIENT'}
    )
    wallet, _ = Wallet.objects.get_or_create(user=launder_user)
    for _ in range(8):
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='CREDIT',
            amount=Decimal('15000.00'),
            source='RECHARGE',
            description='External Transfer',
            balance_after=Decimal('15000.00')
        )

    # --- 3. Rider Performance ---
    print("Tuning Rider Efficiency metrics...")
    riders = RiderProfile.objects.filter(status='APPROVED')[:3]
    for rider_profile in riders:
        rider = rider_profile.rider
        # Give them some varied deliveries
        efficiency_factor = random.choice([15, 45, 60]) # fast, slow, very slow
        
        for _ in range(5):
            placed = timezone.now() - timedelta(hours=random.randint(2, 48))
            pickup = placed + timedelta(minutes=10)
            delivered = pickup + timedelta(minutes=efficiency_factor)
            
            Order.objects.create(
                user=User.objects.filter(role='CLIENT').first(),
                restaurant=Restaurant.objects.first(),
                rider=rider,
                total=Decimal('500.00'),
                subtotal=Decimal('500.00'),
                status='DELIVERED',
                payment_status='PAID',
                placed_at=placed,
                picked_up_at=pickup,
                delivered_at=delivered,
                 delivery_latitude=Decimal('0'), delivery_longitude=Decimal('0'), delivery_phone='000',
                delivery_address='Test Address'
            )

    print("Analytics Data Injection Complete! 🚀")

if __name__ == '__main__':
    populate_analytics()
