from django.db.models.signals import post_save
from django.dispatch import receiver
from client.models import Order
from .models import RestaurantEarnings
from django.utils import timezone


from decimal import Decimal

@receiver(post_save, sender=Order)
def create_restaurant_earning(sender, instance, created, **kwargs):
    """Create restaurant earning when order is delivered"""
    if instance.status == 'DELIVERED' and instance.payment_status == 'PAID':
        # Check if earning already exists
        if not RestaurantEarnings.objects.filter(order=instance).exists():
            commission_rate = Decimal(str(instance.restaurant.commission_rate))
            total = Decimal(str(instance.total))
            commission = (total * commission_rate) / Decimal('100')
            net_amount = total - commission
            
            RestaurantEarnings.objects.create(
                restaurant=instance.restaurant,
                order=instance,
                order_total=instance.total,
                commission=commission,
                net_amount=net_amount,
                date=timezone.now().date()
            )

