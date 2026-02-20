import os
import sys
import django
import random

# Add project root to sys.path
sys.path.append(os.getcwd())

from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import User
from client.models import Wallet, WalletTransaction, Restaurant, Order
from restaurant.models import RestaurantEarnings

def populate():
    print("Starting finance data population...")
    
    # 1. Get Users and ensure they have Wallets
    clients = User.objects.filter(role='CLIENT')
    if not clients.exists():
        print("No clients found. Please create some users first.")
        return
    
    for client in clients:
        Wallet.objects.get_or_create(user=client)
    
    # 2. Generate 25 Wallet Transactions
    sources = ['REFUND', 'RECHARGE', 'ORDER_PAYMENT', 'CASHBACK', 'ADMIN']
    types = ['CREDIT', 'DEBIT']
    
    current_count = WalletTransaction.objects.count()
    if current_count < 25:
        to_create = 25 - current_count
        print(f"Creating {to_create} Wallet Transactions...")
        for i in range(to_create):
            client = random.choice(clients)
            wallet = client.wallet
            tx_type = random.choice(types)
            amount = Decimal(random.randint(50, 500))
            source = random.choice(sources)
            
            # Adjust description based on source
            desc = f"Test {source.replace('_', ' ').title()}"
            if source == 'ORDER_PAYMENT':
                desc = f"Payment for Order #{random.randint(1000, 9999)}"
            
            # Update balance after
            if tx_type == 'CREDIT':
                wallet.balance = Decimal(str(wallet.balance)) + amount
            else:
                wallet.balance = max(Decimal('0.00'), Decimal(str(wallet.balance)) - amount)
            wallet.save()
            
            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type=tx_type,
                amount=amount,
                source=source,
                description=desc,
                balance_after=wallet.balance,
                created_at=timezone.now() - timedelta(days=random.randint(0, 30))
            )
    else:
        print("Wallet Transactions already have 25+ records.")

    # 3. Generate 25 Restaurant Earnings
    restaurants = Restaurant.objects.all()
    orders = Order.objects.filter(status='DELIVERED')
    
    if not restaurants.exists() or not orders.exists():
        print("Need both restaurants and delivered orders to generate earnings.")
        return

    current_earnings = RestaurantEarnings.objects.count()
    if current_earnings < 25:
        to_create = 25 - current_earnings
        print(f"Creating {to_create} Restaurant Earnings...")
        for i in range(to_create):
            rest = random.choice(restaurants)
            order = random.choice(orders)
            total = order.total if order.total > 0 else Decimal(random.randint(200, 1000))
            comm = total * Decimal('0.15')
            net = total - comm
            
            RestaurantEarnings.objects.create(
                restaurant=rest,
                order=order,
                order_total=total,
                commission=comm,
                net_amount=net,
                date=(timezone.now() - timedelta(days=random.randint(0, 30))).date(),
                created_at=timezone.now() - timedelta(days=random.randint(0, 30))
            )
    else:
        print("Restaurant Earnings already have 25+ records.")

    print("Population complete!")

if __name__ == "__main__":
    populate()
