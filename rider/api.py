from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from .decorators import rider_required
from .models import Rider, OrderAssignment
from client.models import Order
from django.urls import reverse

class RiderPollingAPI(View):
    @method_decorator(rider_required)
    def get(self, request):
        email = request.session.get('rider_email')
        if not email and request.user.is_authenticated:
            email = request.user.email
        rider = Rider.objects.get(email=email)
        
        # 1. Active Assignment
        active = OrderAssignment.objects.filter(
            rider=rider, 
            status__in=['ACCEPTED', 'PICKED_UP', 'ON_THE_WAY']
        ).first()
        
        active_data = None
        if active:
            try:
                order = Order.objects.get(id=active.order_id)
                active_data = {
                    'id': active.id,
                    'order_id': order.id,
                    'order_display_id': order.order_id,
                    'status': active.status,
                    'restaurant_name': order.restaurant.name,
                    'restaurant_address': order.restaurant.address,
                    'delivery_address': order.delivery_address,
                    'action_url': reverse('rider:order_action', args=[active.id])
                }
            except Order.DoesNotExist:
                pass

        # 2. Specific Ping (Assigned directly)
        ping = OrderAssignment.objects.filter(rider=rider, status='ASSIGNED').first()
        ping_data = None
        if ping:
            ping_data = {
                'id': ping.id,
                'order_id': ping.order_id,
                'action_url': reverse('rider:order_action', args=[ping.id])
            }

        # 3. Available Broadcasts
        available_pings = []
        if not active and rider.is_online:
            accepted_order_ids = OrderAssignment.objects.filter(
                status__in=['ACCEPTED', 'PICKED_UP', 'ON_THE_WAY']
            ).values_list('order_id', flat=True)
            
            orders = Order.objects.filter(
                restaurant__city__iexact=rider.city,
                status__in=['CONFIRMED', 'PREPARING', 'READY'],
                rider__isnull=True
            ).exclude(id__in=accepted_order_ids).order_by('-placed_at')
            
            for o in orders:
                available_pings.append({
                    'id': o.id,
                    'order_id': o.order_id,
                    'restaurant_name': o.restaurant.name,
                    'accept_url': reverse('rider:accept_order', args=[o.id])
                })

        return JsonResponse({
            'is_online': rider.is_online,
            'active_assignment': active_data,
            'ping_assignment': ping_data,
            'available_pings': available_pings,
            'wallet_balance': float(rider.wallet_balance)
        })
