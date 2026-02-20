from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from datetime import timedelta
from .models import Order
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()


@shared_task
def assign_rider_to_order(order_id):
    """Automatically assign nearest rider to order within the same city"""
    try:
        order = Order.objects.get(id=order_id, status='READY', rider__isnull=True)
        
        from rider.models import Rider, OrderAssignment
        from geopy.distance import distance
        
        # Get online riders in the same city
        online_riders = Rider.objects.filter(
            is_online=True,
            is_active=True,
            city=order.restaurant.city,
            current_latitude__isnull=False,
            current_longitude__isnull=False
        )
        
        if not online_riders.exists():
            return {'status': 'no_riders_available_in_city'}
        
        restaurant_location = (float(order.restaurant.latitude), float(order.restaurant.longitude))
        best_rider = None
        min_distance = float('inf')
        
        for rider in online_riders:
            rider_location = (float(rider.current_latitude), float(rider.current_longitude))
            dist = distance(restaurant_location, rider_location).km
            
            # Check if rider has active orders via OrderAssignment
            active_assignments_count = OrderAssignment.objects.filter(
                rider=rider,
                status__in=['ACCEPTED', 'PICKED_UP', 'ON_THE_WAY']
            ).count()
            
            if dist < min_distance and active_assignments_count < 3:
                min_distance = dist
                best_rider = rider
        
        if best_rider and min_distance <= 10:  # 10km radius for city-wide
            from core.models import User
            try:
                rider_user = User.objects.get(phone=best_rider.phone, role='RIDER')
                
                # We do NOT set order.rider or order.status yet.
                # This allows other riders to still see the order as AVAILABLE.
                
                # Create OrderAssignment record (This will show up as a Ping for this specific rider)
                OrderAssignment.objects.create(
                    rider=best_rider,
                    order_id=order.id,
                    status='ASSIGNED'
                )
                
                # Send notifications to Client
                async_to_sync(channel_layer.group_send)(
                    f'notifications_{order.user.id}',
                    {
                        'type': 'notification_message',
                        'message': {
                            'type': 'rider_assigned',
                            'order_id': order.order_id,
                            'message': f'Rider {best_rider.full_name} has been assigned to your order'
                        }
                    }
                )
                
                # Send notification to assigned Rider
                async_to_sync(channel_layer.group_send)(
                    f'notifications_{rider_user.id}',
                    {
                        'type': 'notification_message',
                        'message': {
                            'type': 'new_assignment',
                            'order_id': order.order_id,
                            'message': f'You have a new order assignment from {order.restaurant.name}'
                        }
                    }
                )
                
                # Notify Restaurant
                async_to_sync(channel_layer.group_send)(
                    f'restaurant_{order.restaurant.owner.id}',
                    {
                        'type': 'order_assigned',
                        'order_id': order.order_id,
                        'rider_name': best_rider.full_name
                    }
                )
                
                return {'status': 'assigned', 'rider_phone': best_rider.phone}
            except User.DoesNotExist:
                return {'status': 'rider_user_missing'}
        
        return {'status': 'no_suitable_rider'}
        
    except Order.DoesNotExist:
        return {'status': 'order_not_found'}


@shared_task
def cancel_unpaid_orders():
    """Cancel orders that are unpaid after 30 minutes"""
    thirty_minutes_ago = timezone.now() - timedelta(minutes=30)
    
    unpaid_orders = Order.objects.filter(
        status='PENDING',
        payment_status='PENDING',
        payment_method='RAZORPAY',
        placed_at__lt=thirty_minutes_ago
    )
    
    cancelled_count = 0
    for order in unpaid_orders:
        order.status = 'CANCELLED'
        order.cancelled_at = timezone.now()
        order.save()
        cancelled_count += 1
    
    return {'cancelled_count': cancelled_count}


@shared_task
def update_restaurant_ratings():
    """Update restaurant ratings based on reviews"""
    from .models import Restaurant, Review
    
    restaurants = Restaurant.objects.all()
    for restaurant in restaurants:
        reviews = Review.objects.filter(restaurant=restaurant)
        if reviews.exists():
            avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
            restaurant.rating = avg_rating or 0
            restaurant.total_ratings = reviews.count()
            restaurant.save()
    
    return {'updated_count': restaurants.count()}


@shared_task
def send_order_reminders():
    """Send reminders for orders that are taking too long"""
    from .models import Order
    
    # Orders that have been preparing for more than 45 minutes
    long_preparing = Order.objects.filter(
        status='PREPARING',
        preparing_at__lt=timezone.now() - timedelta(minutes=45)
    )
    
    for order in long_preparing:
        async_to_sync(channel_layer.group_send)(
            f'notifications_{order.user.id}',
            {
                'type': 'notification_message',
                'message': {
                    'type': 'order_delay',
                    'order_id': order.order_id,
                    'message': f'Your order {order.order_id} is taking longer than expected. We apologize for the delay.'
                }
            }
        )
    
    return {'reminders_sent': long_preparing.count()}


@shared_task
def update_trending_items():
    """Update trending items based on recent orders"""
    from .models import MenuItem, OrderItem
    from datetime import timedelta
    
    week_ago = timezone.now() - timedelta(days=7)
    recent_orders = Order.objects.filter(
        placed_at__gte=week_ago,
        status='DELIVERED'
    )
    
    order_items = OrderItem.objects.filter(order__in=recent_orders)
    trending = order_items.values('menu_item').annotate(
        order_count=Count('id')
    ).order_by('-order_count')[:20]
    
    # Reset trending flag
    MenuItem.objects.update(trending=False)
    
    # Mark trending items
    for item_data in trending:
        try:
            menu_item = MenuItem.objects.get(id=item_data['menu_item'])
            menu_item.trending = True
            menu_item.save()
        except MenuItem.DoesNotExist:
            pass
    
    return {'trending_items_updated': len(trending)}


@shared_task
def cleanup_old_otps():
    """Clean up expired OTPs"""
    from core.models import OTP
    
    expired_otps = OTP.objects.filter(expires_at__lt=timezone.now())
    count = expired_otps.count()
    expired_otps.delete()
    
    return {'deleted_count': count}


@shared_task
def generate_daily_reports():
    """Generate daily reports for restaurants and admin"""
    from restaurant.models import RestaurantEarnings
    from rider.models import RiderEarnings
    from .models import Order
    from datetime import date
    
    yesterday = date.today() - timedelta(days=1)
    
    # Restaurant earnings summary
    restaurant_earnings = RestaurantEarnings.objects.filter(date=yesterday).aggregate(
        total=Sum('net_amount'),
        count=Count('id')
    )
    
    # Rider earnings summary
    rider_earnings = RiderEarnings.objects.filter(date=yesterday).aggregate(
        total=Sum('total_earning'),
        count=Count('id')
    )
    
    # Order summary
    orders = Order.objects.filter(placed_at__date=yesterday)
    order_summary = {
        'total': orders.count(),
        'delivered': orders.filter(status='DELIVERED').count(),
        'cancelled': orders.filter(status='CANCELLED').count(),
        'revenue': float(orders.filter(payment_status='PAID').aggregate(total=Sum('total'))['total'] or 0)
    }
    
    return {
        'date': str(yesterday),
        'restaurant_earnings': restaurant_earnings,
        'rider_earnings': rider_earnings,
        'orders': order_summary
    }
