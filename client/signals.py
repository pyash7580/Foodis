from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Order
from core.city_utils import normalize_city_name

@receiver(post_save, sender=Order)
def order_status_notification(sender, instance, created, **kwargs):
    """
    Triggers WebSocket notifications for status changes.
    """
    channel_layer = get_channel_layer()
    
    # 1. Notify the User (Client) Always
    async_to_sync(channel_layer.group_send)(
        f'notifications_{instance.user.id}',
        {
            'type': 'notification_message',
            'message': {
                'type': 'order_status_update',
                'order_id': instance.order_id,
                'status': instance.status,
                'message': f'Your order is now {instance.get_status_display()}'
            }
        }
    )
    
    # 2. Notify Riders in the City (Broadcast) for Ready/Confirmed orders
    if instance.status in ['CONFIRMED', 'READY'] and not instance.rider:
        city = normalize_city_name(instance.restaurant.city)
        async_to_sync(channel_layer.group_send)(
            f'rider_assignments_{city}',
            {
                'type': 'notification_message',
                'message': {
                    'type': 'new_order_available',
                    'order_id': instance.id,
                    'order_display_id': instance.order_id,
                    'restaurant_name': instance.restaurant.name,
                    'city': city,
                    'message': 'New delivery mission available nearby!'
                }
            }
        )
    
    # 3. Notify Specifically Assigned Rider
    if instance.rider:
        rider_id = instance.rider.id
        if instance.status == 'ASSIGNED':
            async_to_sync(channel_layer.group_send)(
                f'notifications_{rider_id}',
                {
                    'type': 'notification_message',
                    'message': {
                        'type': 'order_assigned',
                        'order_id': instance.id,
                        'order_display_id': instance.order_id,
                        'message': 'A new mission has been assigned to you!'
                    }
                }
            )
        elif instance.status == 'CANCELLED':
            async_to_sync(channel_layer.group_send)(
                f'notifications_{rider_id}',
                {
                    'type': 'notification_message',
                    'message': {
                        'type': 'order_cancelled',
                        'order_id': instance.order_id,
                        'message': f'Mission {instance.order_id} has been cancelled by the customer/restaurant.'
                    }
                }
            )
