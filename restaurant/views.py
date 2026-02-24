from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from client.models import Restaurant, MenuItem, MenuItemCustomization, CustomizationOption, Order, OrderItem
from .models import RestaurantProfile, RestaurantEarnings, OrderStatusUpdate
from .serializers import (
    RestaurantSerializer, RestaurantProfileSerializer, MenuItemSerializer,
    MenuItemCustomizationSerializer, CustomizationOptionSerializer,
    OrderSerializer, RestaurantEarningsSerializer, OrderStatusUpdateSerializer,
    CouponSerializer
)
from client.models import Restaurant, MenuItem, MenuItemCustomization, CustomizationOption, Order, OrderItem, Coupon
from core.utils import generate_otp, broadcast_order_status
from ai_engine.utils import get_restaurant_insights
from client.services.otp_service import OTPService

channel_layer = get_channel_layer()
logger = logging.getLogger(__name__)


class RestaurantViewSet(viewsets.ModelViewSet):
    """ViewSet for Restaurant Management"""
    serializer_class = RestaurantSerializer

    def _safe_restaurant_data(self, restaurant, request):
        """Serialize restaurant defensively to avoid breaking dashboard on bad records."""
        try:
            return RestaurantSerializer(restaurant, context={'request': request}).data
        except Exception:
            logger.exception("Failed to serialize restaurant id=%s", getattr(restaurant, "id", None))
            return {
                'id': restaurant.id,
                'name': restaurant.name,
                'slug': restaurant.slug,
                'status': restaurant.status,
                'city': restaurant.city,
                'state': restaurant.state,
                'pincode': restaurant.pincode,
                'phone': restaurant.phone,
                'email': restaurant.email,
                'address': restaurant.address,
                'delivery_time': restaurant.delivery_time,
                'delivery_fee': restaurant.delivery_fee,
                'min_order_amount': restaurant.min_order_amount,
                'is_active': restaurant.is_active,
                'rating': restaurant.rating,
                'total_ratings': restaurant.total_ratings,
                'profile': None,
            }

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Restaurant.objects.none()
        if user.role == 'ADMIN':
            return Restaurant.objects.all()
        return Restaurant.objects.filter(owner=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = [self._safe_restaurant_data(restaurant, request) for restaurant in queryset]
        return Response(data, status=status.HTTP_200_OK)
    def create(self, request, *args, **kwargs):
        """Handle restaurant creation or update if already exists for owner"""
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        if restaurant:
            # Update existing restaurant WITHOUT resetting status to PENDING
            # This allows owners to update details/images without going offline
            serializer = self.get_serializer(restaurant, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Standard creation
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, status='PENDING')
    
    @action(detail=True, methods=['get', 'put'])
    def profile(self, request, pk=None):
        """Get or update restaurant profile"""
        restaurant = self.get_object()
        profile, created = RestaurantProfile.objects.get_or_create(restaurant=restaurant)
        
        if request.method == 'PUT':
            serializer = RestaurantProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RestaurantProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get restaurant statistics"""
        restaurant = self.get_object()
        
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Orders
        total_orders = Order.objects.filter(restaurant=restaurant).count()
        today_orders = Order.objects.filter(restaurant=restaurant, placed_at__date=today).count()
        week_orders = Order.objects.filter(restaurant=restaurant, placed_at__date__gte=week_ago).count()
        month_orders = Order.objects.filter(restaurant=restaurant, placed_at__date__gte=month_ago).count()
        
        # Earnings
        total_earnings = RestaurantEarnings.objects.filter(restaurant=restaurant).aggregate(
            total=Sum('net_amount')
        )['total'] or Decimal('0.00')
        
        today_earnings = RestaurantEarnings.objects.filter(
            restaurant=restaurant, date=today
        ).aggregate(total=Sum('net_amount'))['total'] or Decimal('0.00')
        
        week_earnings = RestaurantEarnings.objects.filter(
            restaurant=restaurant, date__gte=week_ago
        ).aggregate(total=Sum('net_amount'))['total'] or Decimal('0.00')
        
        # Pending orders
        pending_orders = Order.objects.filter(
            restaurant=restaurant,
            status__in=['PENDING', 'CONFIRMED', 'PREPARING']
        ).count()
        
        # Graph Data (Last 7 days)
        graph_data = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            day_orders = Order.objects.filter(restaurant=restaurant, placed_at__date=date)
            graph_data.append({
                'name': date.strftime('%a'),
                'orders': day_orders.count(),
                'earnings': float(RestaurantEarnings.objects.filter(restaurant=restaurant, date=date).aggregate(Sum('net_amount'))['total'] or 0)
            })
        
        return Response({
            'orders': {
                'total': total_orders,
                'today': today_orders,
                'week': week_orders,
                'month': month_orders,
                'pending': pending_orders
            },
            'earnings': {
                'total': float(total_earnings),
                'today': float(today_earnings),
                'week': float(week_earnings)
            },
            'graph_data': graph_data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def ai_insights(self, request, pk=None):
        """Get AI-powered insights for the restaurant"""
        restaurant = self.get_object()
        insights = get_restaurant_insights(restaurant)
        return Response(insights, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary stats for the current user's restaurant"""
        restaurant = Restaurant.objects.filter(owner=request.user).first()
        if not restaurant:
            return Response({'error': 'Restaurant not found'}, status=status.HTTP_404_NOT_FOUND)
            
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Orders
        total_orders = Order.objects.filter(restaurant=restaurant).count()
        today_orders = Order.objects.filter(restaurant=restaurant, placed_at__date=today).count()
        week_orders = Order.objects.filter(restaurant=restaurant, placed_at__date__gte=week_ago).count()
        month_orders = Order.objects.filter(restaurant=restaurant, placed_at__date__gte=month_ago).count()
        
        # Earnings
        total_earnings = RestaurantEarnings.objects.filter(restaurant=restaurant).aggregate(
            total=Sum('net_amount')
        )['total'] or Decimal('0.00')
        
        today_earnings = RestaurantEarnings.objects.filter(
            restaurant=restaurant, date=today
        ).aggregate(total=Sum('net_amount'))['total'] or Decimal('0.00')
        
        week_earnings = RestaurantEarnings.objects.filter(
            restaurant=restaurant, date__gte=week_ago
        ).aggregate(total=Sum('net_amount'))['total'] or Decimal('0.00')
        
        # Pending orders
        pending_orders = Order.objects.filter(
            restaurant=restaurant,
            status__in=['PENDING', 'CONFIRMED', 'PREPARING']
        ).count()
        
        # Graph Data (Last 7 days)
        graph_data = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            day_orders = Order.objects.filter(restaurant=restaurant, placed_at__date=date)
            graph_data.append({
                'name': date.strftime('%a'),
                'orders': day_orders.count(),
                'earnings': float(RestaurantEarnings.objects.filter(restaurant=restaurant, date=date).aggregate(total=Sum('net_amount'))['total'] or 0)
            })
            
        return Response({
            'restaurant': self._safe_restaurant_data(restaurant, request),
            'orders': {
                'total': total_orders,
                'today': today_orders,
                'week': week_orders,
                'month': month_orders,
                'pending': pending_orders
            },
            'earnings': {
                'total': float(total_earnings),
                'today': float(today_earnings),
                'week': float(week_earnings)
            },
            'graph_data': graph_data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def insights(self, request, pk=None):
        """Get AI insights for restaurant"""
        restaurant = self.get_object()
        insights = get_restaurant_insights(restaurant)
        return Response(insights, status=status.HTTP_200_OK)


class MenuItemViewSet(viewsets.ModelViewSet):
    """ViewSet for Menu Item Management"""
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        if restaurant:
            return MenuItem.objects.filter(restaurant=restaurant)
        return MenuItem.objects.none()
    
    def perform_create(self, serializer):
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        if restaurant:
            serializer.save(restaurant=restaurant)
        else:
            raise serializers.ValidationError("Restaurant not found")
    
    @action(detail=True, methods=['post'])
    def toggle_availability(self, request, pk=None):
        """Toggle menu item availability"""
        menu_item = self.get_object()
        menu_item.is_available = not menu_item.is_available
        menu_item.save()
        serializer = MenuItemSerializer(menu_item, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class MenuItemCustomizationViewSet(viewsets.ModelViewSet):
    """ViewSet for Menu Item Customizations"""
    serializer_class = MenuItemCustomizationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        if restaurant:
            menu_items = MenuItem.objects.filter(restaurant=restaurant)
            return MenuItemCustomization.objects.filter(menu_item__in=menu_items)
        return MenuItemCustomization.objects.none()
    
    def perform_create(self, serializer):
        menu_item_id = self.request.data.get('menu_item')
        menu_item = MenuItem.objects.get(id=menu_item_id)
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        
        if menu_item.restaurant != restaurant:
            raise serializers.ValidationError("Invalid menu item")
        
        serializer.save(menu_item=menu_item)


class CustomizationOptionViewSet(viewsets.ModelViewSet):
    """ViewSet for Customization Options"""
    serializer_class = CustomizationOptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        if restaurant:
            menu_items = MenuItem.objects.filter(restaurant=restaurant)
            customizations = MenuItemCustomization.objects.filter(menu_item__in=menu_items)
            return CustomizationOption.objects.filter(customization__in=customizations)
        return CustomizationOption.objects.none()
    
    def perform_create(self, serializer):
        customization_id = self.request.data.get('customization')
        customization = MenuItemCustomization.objects.get(id=customization_id)
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        
        if customization.menu_item.restaurant != restaurant:
            raise serializers.ValidationError("Invalid customization")
        
        serializer.save(customization=customization)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Restaurant Orders"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'order_id'
    
    def get_queryset(self):
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        if restaurant:
            return Order.objects.filter(restaurant=restaurant).exclude(status='CANCELLED')
        return Order.objects.none()
    
    @action(detail=True, methods=['post'])
    def accept(self, request, order_id=None):
        """Accept order"""
        order = self.get_object()
        
        if order.status != 'PENDING':
            return Response({'error': 'Order cannot be accepted'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'CONFIRMED'
        order.confirmed_at = timezone.now()
        order.save()
        
        # Create status update
        OrderStatusUpdate.objects.create(
            order=order,
            status='CONFIRMED',
            updated_by=request.user,
            notes='Order accepted by restaurant'
        )
        
        # Send notification to client
        async_to_sync(channel_layer.group_send)(
            f'notifications_{order.user.id}',
            {
                'type': 'notification_message',
                'message': {
                    'type': 'order_confirmed',
                    'order_id': order.order_id,
                    'message': f'Your order {order.order_id} has been confirmed'
                }
            }
        )
        
        # Broadcast status change
        broadcast_order_status(order)

        # 📌 GENERATE/RETRIEVE PICKUP OTP EARLY
        # Since riders can see CONFIRMED orders, they might arrive early.
        # We use already existing if valid, otherwise generate
        from client.services.otp_service import OTPService
        otp = OTPService.get_valid_otp(order, 'PICKUP')
        if not otp:
            otp = OTPService.generate_otp(order, 'PICKUP')
        
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, order_id=None):
        """Reject order"""
        order = self.get_object()
        reason = request.data.get('reason', '')
        
        if order.status != 'PENDING':
            return Response({'error': 'Order cannot be rejected'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'CANCELLED'
        order.cancelled_at = timezone.now()
        order.save()
        
        # Create status update
        OrderStatusUpdate.objects.create(
            order=order,
            status='CANCELLED',
            updated_by=request.user,
            notes=f'Order rejected: {reason}'
        )
        
        # Refund if paid
        if order.payment_status == 'PAID' and order.payment_method != 'COD':
            from client.models import Wallet, WalletTransaction
            wallet, _ = Wallet.objects.get_or_create(user=order.user)
            wallet.balance += order.total
            wallet.save()
            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type='CREDIT',
                amount=order.total,
                source='REFUND',
                order=order,
                balance_after=wallet.balance
            )
            order.payment_status = 'REFUNDED'
            order.save()
        
        # Send notification to client
        async_to_sync(channel_layer.group_send)(
            f'notifications_{order.user.id}',
            {
                'type': 'notification_message',
                'message': {
                    'type': 'order_rejected',
                    'order_id': order.order_id,
                    'message': f'Your order {order.order_id} has been rejected'
                }
            }
        )
        
        # Broadcast status change
        broadcast_order_status(order)
        
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def start_preparing(self, request, order_id=None):
        """Start preparing order"""
        order = self.get_object()
        
        if order.status not in ['CONFIRMED', 'PREPARING', 'ASSIGNED']:
            return Response({'error': 'Invalid order status'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'PREPARING'
        order.preparing_at = timezone.now()
        order.save()
        
        OrderStatusUpdate.objects.create(
            order=order,
            status='PREPARING',
            updated_by=request.user,
            notes='Order preparation started'
        )
        
        # Broadcast status change
        broadcast_order_status(order)
        
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def mark_ready(self, request, order_id=None):
        """Mark order as ready for pickup"""
        order = self.get_object()
        
        if order.status not in ['PREPARING', 'ASSIGNED']:
            return Response({'error': 'Order is not being prepared'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'READY'
        order.ready_at = timezone.now()
        # NOTE: We do NOT generate OTP here anymore. 
        # OTP is generated when rider arrives via generate_pickup_otp
        order.save()
        
        OrderStatusUpdate.objects.create(
            order=order,
            status='READY',
            updated_by=request.user,
            notes='Order ready for pickup'
        )
        
        
        # Generate/Retrieve Pickup OTP
        # Use existing if still valid, otherwise generate new one
        otp = OTPService.get_valid_otp(order, 'PICKUP')
        if not otp:
            otp = OTPService.generate_otp(order, 'PICKUP')
        
        # Send notification to assign rider in the specific city
        async_to_sync(channel_layer.group_send)(
            f'rider_assignments_{order.restaurant.city}',
            {
                'type': 'new_order_ready',
                'order_id': order.order_id,
                'restaurant_location': {
                    'latitude': float(order.restaurant.latitude),
                    'longitude': float(order.restaurant.longitude)
                },
                'delivery_location': {
                    'latitude': float(order.delivery_latitude),
                    'longitude': float(order.delivery_longitude)
                }
            }
        )
        
        # Broadcast status change
        broadcast_order_status(order)
        
        serializer = OrderSerializer(order, context={'request': request})
        # Inject OTP into response for immediate display
        response_data = serializer.data
        response_data['pickup_otp'] = otp
        
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def generate_pickup_otp(self, request, order_id=None):
        """Regenerate pickup OTP for rider"""
        order = self.get_object()
        
        # Allow generating OTP if status is READY or ASSIGNED or WAITING_FOR_RIDER
        if order.status not in ['READY', 'ASSIGNED', 'WAITING_FOR_RIDER']:
            return Response({'error': 'Order not ready for pickup'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        otp = OTPService.generate_otp(order, 'PICKUP')
        
        return Response({'pickup_otp': otp}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def get_pickup_otp(self, request, order_id=None):
        """Get current valid pickup OTP (if any)"""
        order = self.get_object()
        
        if order.status not in ['READY', 'ASSIGNED', 'WAITING_FOR_RIDER']:
             return Response({'error': 'OTP not available for this status'}, 
                           status=status.HTTP_400_BAD_REQUEST)

        otp = OTPService.get_valid_otp(order, 'PICKUP')
        
        if not otp:
             return Response({'error': 'OTP expired or not visible. Please regenerate.'}, 
                           status=status.HTTP_404_NOT_FOUND)
            
        return Response({'pickup_otp': otp}, status=status.HTTP_200_OK)


class RestaurantEarningsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Restaurant Earnings"""
    serializer_class = RestaurantEarningsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        if restaurant:
            return RestaurantEarnings.objects.filter(restaurant=restaurant)
        return RestaurantEarnings.objects.none()
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get earnings summary"""
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        if not restaurant:
            return Response({'error': 'Restaurant not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        today_earnings = RestaurantEarnings.objects.filter(
            restaurant=restaurant, date=today
        ).aggregate(total=Sum('net_amount'))['total'] or Decimal('0.00')
        
        week_earnings = RestaurantEarnings.objects.filter(
            restaurant=restaurant, date__gte=week_ago
        ).aggregate(total=Sum('net_amount'))['total'] or Decimal('0.00')
        
        month_earnings = RestaurantEarnings.objects.filter(
            restaurant=restaurant, date__gte=month_ago
        ).aggregate(total=Sum('net_amount'))['total'] or Decimal('0.00')
        
        return Response({
            'today': float(today_earnings),
            'week': float(week_earnings),
            'month': float(month_earnings)
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def download_csv(self, request):
        """Download earnings as CSV"""
        import csv
        from django.http import HttpResponse
        
        restaurant = Restaurant.objects.filter(owner=request.user).first()
        if not restaurant:
            return Response({'error': 'Restaurant not found'}, status=status.HTTP_404_NOT_FOUND)
            
        earnings = RestaurantEarnings.objects.filter(restaurant=restaurant).order_by('-date')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="earnings_{restaurant.slug}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Order ID', 'Order Total', 'Commission', 'Net Amount'])
        
        for record in earnings:
            writer.writerow([
                record.date,
                record.order.order_id,
                record.order_total,
                record.commission,
                record.net_amount
            ])
            
        return response


class CouponViewSet(viewsets.ModelViewSet):
    """ViewSet for Coupon Management"""
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Return all active coupons. 
        # In a real app, you might want to scope this, but model is global.
        return Coupon.objects.filter(is_active=True).order_by('-created_at')
    
    def perform_create(self, serializer):
        # Set default expiry if not provided (e.g. 30 days)
        valid_from = self.request.data.get('valid_from')
        valid_until = self.request.data.get('valid_until')
        
        if not valid_from:
            valid_from = timezone.now()
        
        if not valid_until:
             valid_until = timezone.now() + timedelta(days=30)
             
        serializer.save(valid_from=valid_from, valid_until=valid_until)

