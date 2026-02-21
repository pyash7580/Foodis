from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count, Sum, Prefetch
from django.db import transaction
from geopy.distance import distance
from decimal import Decimal
import razorpay
import os
import logging
from django.conf import settings
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from core.utils import broadcast_order_status
from client.services.otp_service import OTPService

logger = logging.getLogger(__name__)

from .models import (
    Category, Restaurant, MenuItem, Cart, CartItem, Order, OrderItem,
    Coupon, Wallet, WalletTransaction, Review,
    SavedPaymentMethod, FavouriteRestaurant, FavouriteMenuItem
)
from .serializers import (
    CategorySerializer, RestaurantSerializer, RestaurantDetailSerializer,
    MenuItemSerializer, CartSerializer, CartItemSerializer, OrderSerializer,
    CouponSerializer, WalletSerializer, WalletTransactionSerializer, ReviewSerializer,
    SavedPaymentMethodSerializer, FavouriteRestaurantSerializer, FavouriteMenuItemSerializer
)
from core.serializers import UserSerializer, AddressSerializer
from rider_legacy.models import RiderReview, RiderProfile
from rider_legacy.serializers import RiderReviewSerializer
from core.models import Address
from core.city_utils import normalize_city_name
from ai_engine.utils import get_recommendations, get_trending_items

channel_layer = get_channel_layer()


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Categories"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class RestaurantViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Restaurants"""
    queryset = Restaurant.objects.filter(status='APPROVED', is_active=True)
    serializer_class = RestaurantSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_veg']
    search_fields = ['name', 'description', 'city', 'menu_items__name', 'menu_items__description']
    ordering_fields = ['rating', 'delivery_time', 'created_at']
    ordering = ['-rating']
    
    def get_queryset(self):
        queryset = Restaurant.objects.filter(status='APPROVED', is_active=True)

        # Add select_related for foreign keys to avoid N+1 queries
        queryset = queryset.select_related('city_id')

        # Prefetch menu items and categories to avoid N+1 queries
        queryset = queryset.prefetch_related('menu_items__category')

        # Annotate menu items count to avoid individual count() queries in serializer
        queryset = queryset.annotate(menu_items_count_cached=Count('menu_items', distinct=True))

        city = self.request.query_params.get('city')

        if city:
            normalized_city = normalize_city_name(city)
            queryset = queryset.filter(
                Q(city__iexact=normalized_city) |
                Q(city_id__name__iexact=normalized_city)
            )

        latitude = self.request.query_params.get('latitude')
        longitude = self.request.query_params.get('longitude')
        radius = float(self.request.query_params.get('radius', 80)) # Default 80km

        if latitude and longitude:
            try:
                user_location = (float(latitude), float(longitude))

                # First pass: bounding box filter to reduce dataset before expensive distance calculations
                # Approximate: 1 degree latitude ≈ 111km, longitude varies by cos(latitude)
                import math
                lat_delta = radius / 111.0
                lon_delta = radius / (111.0 * math.cos(math.radians(float(latitude))))

                queryset = queryset.filter(
                    latitude__gte=float(latitude) - lat_delta,
                    latitude__lte=float(latitude) + lat_delta,
                    longitude__gte=float(longitude) - lon_delta,
                    longitude__lte=float(longitude) + lon_delta
                )

                # Second pass: precise distance filtering only on the bounding box results
                filtered_ids = []
                for restaurant in queryset:
                    try:
                        res_location = (float(restaurant.latitude), float(restaurant.longitude))
                        if distance(user_location, res_location).km <= radius:
                            filtered_ids.append(restaurant.id)
                    except (ValueError, TypeError):
                        continue
                queryset = queryset.filter(id__in=filtered_ids)
            except (ValueError, TypeError):
                pass

        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Get nearby restaurants"""
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        radius = float(request.query_params.get('radius', 80))  # km
        
        if not latitude or not longitude:
            return Response({'error': 'Latitude and longitude are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_location = (float(latitude), float(longitude))
            restaurants = []
            
            for restaurant in self.queryset:
                try:
                    restaurant_location = (float(restaurant.latitude), float(restaurant.longitude))
                    dist = distance(user_location, restaurant_location).km
                    if dist <= radius:
                        restaurants.append({
                            'restaurant': RestaurantSerializer(restaurant, context={'request': request}).data,
                            'distance': round(dist, 2)
                        })
                except (ValueError, TypeError):
                    pass
            
            # Sort by distance
            restaurants.sort(key=lambda x: x['distance'])
            
            return Response(restaurants, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def menu(self, request, pk=None):
        """Get restaurant menu"""
        restaurant = self.get_object()
        menu_items = MenuItem.objects.filter(restaurant=restaurant, is_available=True).select_related('category')
        serializer = MenuItemSerializer(menu_items, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Get restaurant details"""
        instance = self.get_object()
        # Prefetch menu items with categories for detail view
        from django.db.models import Prefetch
        menu_items = MenuItem.objects.filter(is_available=True).select_related('category')
        instance.menu_items_all = instance.menu_items.filter(
            is_available=True
        ).select_related('category')
        serializer = RestaurantDetailSerializer(instance, context={'request': request})
        return Response(serializer.data)


class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Menu Items"""
    queryset = MenuItem.objects.filter(is_available=True)
    serializer_class = MenuItemSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['restaurant', 'category', 'veg_type']
    search_fields = ['name', 'description']

    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending menu items"""
        trending_items = get_trending_items()
        return Response(trending_items, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """Get personalized recommendations"""
        query = request.query_params.get('query')
        user = request.user if request.user.is_authenticated else None
        recommendations = get_recommendations(query=query, user=user)
        return Response(recommendations, status=status.HTTP_200_OK)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class CartViewSet(viewsets.ModelViewSet):
    """ViewSet for Cart"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart"""
        menu_item_id = request.data.get('menu_item_id')
        quantity = int(request.data.get('quantity', 1))
        customizations = request.data.get('customizations', {})
        
        try:
            menu_item = MenuItem.objects.get(id=menu_item_id, is_available=True)
            
            # Check if user has an active cart
            cart = Cart.objects.filter(user=request.user).first()
            
            if cart:
                # If cart exists but restaurant is different, clear previous items and switch restaurant
                if cart.restaurant != menu_item.restaurant:
                    cart.items.all().delete()
                    cart.restaurant = menu_item.restaurant
                    cart.save()
            else:
                # Create new cart
                cart = Cart.objects.create(user=request.user, restaurant=menu_item.restaurant)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                menu_item=menu_item,
                customizations=customizations,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            serializer = CartSerializer(cart, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except MenuItem.DoesNotExist:
            return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_item(self, request, pk=None):
        """Update cart item quantity"""
        cart = self.get_object()
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            if quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()
            
            serializer = CartSerializer(cart, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['delete'])
    def remove_item(self, request, pk=None):
        """Remove item from cart"""
        cart = self.get_object()
        item_id = request.data.get('item_id')
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
            
            serializer = CartSerializer(cart, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def sync(self, request):
        """Sync entire cart from frontend"""
        restaurant_id = request.data.get('restaurant_id')
        items = request.data.get('items', [])
        
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
            
            # Get or create cart - handle missing restaurant_id for new carts
            cart = Cart.objects.filter(user=request.user).first()
            if not cart:
                cart = Cart.objects.create(user=request.user, restaurant=restaurant)
            
            # Always update restaurant and clear existing items for a fresh sync
            cart.restaurant = restaurant
            cart.items.all().delete()
            cart.save()
            
            # Add new items
            for item in items:
                menu_item = MenuItem.objects.get(id=item.get('id'))
                CartItem.objects.create(
                    cart=cart,
                    menu_item=menu_item,
                    quantity=item.get('quantity', 1),
                    customizations=item.get('customizations', {})
                )
            
            serializer = CartSerializer(cart, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Restaurant.DoesNotExist:
            return Response({'error': 'Restaurant not found'}, status=status.HTTP_404_NOT_FOUND)
        except MenuItem.DoesNotExist:
            return Response({'error': 'One or more menu items not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """Clear cart"""
        cart = self.get_object()
        cart.items.all().delete()
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Orders"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'order_id'
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status']
    ordering = ['-placed_at']
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def create(self, request):
        """Create order from cart"""
        cart_id = request.data.get('cart_id')
        address_id = request.data.get('address_id')
        payment_method = request.data.get('payment_method', 'COD')
        coupon_code = request.data.get('coupon_code')
        delivery_instructions = request.data.get('delivery_instructions', '')
        
        try:
            cart = Cart.objects.get(id=cart_id, user=request.user)
            address = Address.objects.get(id=address_id, user=request.user)
            
            if cart.items.count() == 0:
                return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Calculate totals
            subtotal = cart.total
            delivery_fee = cart.restaurant.delivery_fee
            discount = Decimal('0.00')
            coupon = None
            
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                    if coupon.is_valid(subtotal + delivery_fee):
                        discount = coupon.calculate_discount(subtotal + delivery_fee)
                        # Usage count will be incremented after successful order creation
                except Coupon.DoesNotExist:
                    pass
            
            platform_fee = Decimal('5.00')  # Fixed Zomato-like platform fee
            
            # GST & taxes (5% on food + 18% on platform/delivery)
            tax = (subtotal * Decimal('0.05')) + ((delivery_fee + platform_fee) * Decimal('0.18'))
            total = subtotal + delivery_fee + platform_fee - discount + tax
            
            # Check minimum order amount
            if subtotal < cart.restaurant.min_order_amount:
                return Response({
                    'error': f'Minimum order amount is ₹{cart.restaurant.min_order_amount}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                restaurant=cart.restaurant,
                delivery_address=f"{address.address_line1}, {address.city}, {address.state} - {address.pincode}",
                delivery_latitude=address.latitude,
                delivery_longitude=address.longitude,
                delivery_phone=request.user.phone,
                delivery_instructions=delivery_instructions,
                subtotal=subtotal,
                delivery_fee=delivery_fee,
                discount=discount,
                platform_fee=platform_fee,
                tax=tax,
                total=total,
                coupon=coupon,
                city_id=cart.restaurant.city_id,
                payment_method=payment_method,
                payment_status='PENDING'
            )
            
            # Increment coupon usage if applied
            if coupon:
                coupon.used_count += 1
                coupon.save()
            
            # Create order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    menu_item=cart_item.menu_item,
                    quantity=cart_item.quantity,
                    price=cart_item.menu_item.price,
                    customizations=cart_item.customizations,
                    subtotal=cart_item.subtotal
                )
            
            # Split Payment Logic
            use_wallet = request.data.get('use_wallet', False)
            wallet_amount_deducted = Decimal('0.00')
            online_amount = total
            
            if use_wallet:
                wallet, _ = Wallet.objects.get_or_create(user=request.user)
                if wallet.balance > 0:
                    if wallet.balance >= total:
                        # Full payment via wallet
                        wallet_amount_deducted = total
                        online_amount = Decimal('0.00')
                        wallet.balance -= total
                    else:
                        # Partial payment
                        wallet_amount_deducted = wallet.balance
                        online_amount = total - wallet.balance
                        wallet.balance = Decimal('0.00')
                    
                    wallet.save()
                    
                    # Log Debit Transaction
                    if wallet_amount_deducted > 0:
                        WalletTransaction.objects.create(
                            wallet=wallet, transaction_type='DEBIT', amount=wallet_amount_deducted,
                            source='ORDER_PAYMENT', order=order, balance_after=wallet.balance
                        )

            # Update Order with Split details
            order.wallet_amount = wallet_amount_deducted
            order.online_amount = online_amount
            
            # Handle Payment Status based on split
            if online_amount == 0 and wallet_amount_deducted > 0:
                 order.payment_status = 'PAID'
                 order.status = 'CONFIRMED' # Wallet full payment is instant
                 order.payment_method = 'WALLET' # Override/Set as primary
            
            order.save()

            # Handle Online Payment (Razorpay) for remaining
            if online_amount > 0 and payment_method != 'COD':
                try:
                    if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
                        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                        razorpay_order = client.order.create({
                            'amount': int(online_amount * 100),  # Convert remaining to paise
                            'currency': 'INR',
                            'receipt': order.order_id
                        })
                        order.razorpay_order_id = razorpay_order['id']
                    else:
                        raise Exception("Razorpay keys not configured")
                except Exception as e:
                    # Fallback to Demo Mode
                    logger.warning(f"Razorpay creation failed (Demo Mode active): {e}")
                    order.razorpay_order_id = f"demo_order_{order.order_id}"
                
                order.save()
            
            # Note: We replaced the specific 'WALLET' block with this unified block.
            # The original 'WALLET' block was lines 345-374 which we are removing implicitly by over-writing the RAZORPAY block and covering all cases.
            
            # Wait, the original code had `if payment_method == 'RAZORPAY':` ... `elif payment_method == 'WALLET':`.
            # We are rewriting lines 326-349.
            # We must ensure we don't break COD or pure Wallet flow.
            
            if payment_method == 'COD':
                # No change for COD, logic handled elsewhere (status PENDING)
                pass

            # Clear cart if fully paid or COD
            if online_amount == 0 or payment_method == 'COD':
                cart.items.all().delete()
            
            # Send notification to restaurant
            async_to_sync(channel_layer.group_send)(
                f'restaurant_{cart.restaurant.owner.id}',
                {
                    'type': 'new_order',
                    'order_id': order.order_id,
                    'message': f'New order {order.order_id} received'
                }
            )
            
            serializer = OrderSerializer(order, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        except Address.DoesNotExist:
            return Response({'error': 'Address not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def track(self, request, *args, **kwargs):
        """Track order"""
        order = self.get_object()
        serializer = OrderSerializer(order, context={'request': request})
        data = serializer.data
        
        # Inject Delivery OTP if Order is On the Way
        if order.status == 'ON_THE_WAY':
            otp = OTPService.get_valid_otp(order, 'DELIVERY')
            if otp:
                data['delivery_otp'] = otp
                
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, *args, **kwargs):
        """Cancel order with refund logic"""
        order = self.get_object()
        
        # Check if order can be cancelled
        if order.status in ['DELIVERED', 'CANCELLED', 'REFUNDED', 'PICKED_UP', 'ON_THE_WAY']:
            return Response({'error': f'Cannot cancel order in {order.status} status'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Check cancellation time limit
                if order.placed_at:
                    time_diff = (timezone.now() - order.placed_at).total_seconds() / 60
                    if time_diff > settings.ORDER_CANCELLATION_TIME_LIMIT:
                        return Response({'error': 'Cancellation time limit exceeded'}, 
                                      status=status.HTTP_400_BAD_REQUEST)
                
                reason = request.data.get('reason', 'User cancelled')
                order.status = 'CANCELLED'
                order.cancelled_at = timezone.now()
                order.cancellation_reason = reason
                order.save(update_fields=['status', 'cancelled_at', 'cancellation_reason'])
                
                # Refund logic: If paid and not COD, refund to wallet
                if order.payment_status == 'PAID' and order.payment_method != 'COD':
                    wallet, _ = Wallet.objects.get_or_create(user=request.user)
                    
                    # Store balance before for transaction record
                    original_balance = wallet.balance
                    wallet.balance += Decimal(str(order.total))
                    wallet.save(update_fields=['balance'])
                    
                    WalletTransaction.objects.create(
                        wallet=wallet,
                        transaction_type='CREDIT',
                        amount=order.total,
                        source='REFUND',
                        order=order,
                        balance_after=wallet.balance,
                        description=f"Refund for cancelled order #{order.order_id}"
                    )
                    
                    order.payment_status = 'REFUNDED'
                    order.save(update_fields=['payment_status'])
                
                # Broadcast status update
                broadcast_order_status(order)
            
            serializer = OrderSerializer(order, context={'request': request})
            return Response({
                'message': 'Order cancelled successfully',
                'order': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({
                'error': f"Cancellation Error: {str(e)}",
                'details': traceback.format_exc() if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def verify_payment(self, request, *args, **kwargs):
        """Verify Razorpay payment signature"""
        order = self.get_object()
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_signature = request.data.get('razorpay_signature')
        
        if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
             return Response({'error': 'Missing payment details'}, status=status.HTTP_400_BAD_REQUEST)
             
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Verify signature
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
            
            # Update order
            order.payment_status = 'PAID'
            order.status = 'PENDING'
            order.razorpay_payment_id = razorpay_payment_id
            order.save()

            # Clear Cart on Success
            cart = Cart.objects.filter(user=order.user).first()
            if cart:
                cart.items.all().delete()
            
            # Notify Restaurant
            async_to_sync(channel_layer.group_send)(
                f'restaurant_{order.restaurant.owner.id}',
                {
                    'type': 'new_order',
                    'order_id': order.order_id,
                    'message': f'Order {order.order_id} payment verified'
                }
            )

            # Broadcast status change
            broadcast_order_status(order)

            return Response({'status': 'Payment verified and order ready'}, status=status.HTTP_200_OK)
            
        except razorpay.errors.SignatureVerificationError:
            return Response({'error': 'Payment verification failed'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Payment verification failed for order {order.order_id}: {e}")
            order.payment_status = 'FAILED'
            order.save()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def simulate_payment(self, request, *args, **kwargs):
        """
        DEMO ONLY: Simulate a successful payment without verification.
        """
        try:
            logger.info(f"[DEMO] Simulating Payment for order {self.kwargs.get(self.lookup_field)}")
            
            order = self.get_object()
            logger.debug(f"Order found: {order.order_id}")
            
            order.payment_status = 'PAID'
            order.status = 'PENDING'
            order.razorpay_payment_id = f"demo_pay_{order.id}"
            order.save()

            # Clear Cart on Success (Demo)
            cart = Cart.objects.filter(user=order.user).first()
            if cart:
                cart.items.all().delete()
            
            print(f"Order {order.order_id} updated to PAID/PENDING")

            # Notify Restaurant
            try:
                print(f"Notifying restaurant...")
                async_to_sync(channel_layer.group_send)(
                    f'restaurant_{order.restaurant.owner.id}',
                    {
                        'type': 'new_order',
                        'order_id': order.order_id,
                        'message': f'New paid order {order.order_id} received (Demo)'
                    }
                )
                print(f"Notification sent to restaurant")
            except Exception as e:
                print(f"Error notifying restaurant: {e}")
            
            # Broadcast status change
            broadcast_order_status(order)

            return Response({'status': 'Demo payment successful and order ready'}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"DEMO PAYMENT FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def refund(self, request, *args, **kwargs):
        """
        ADMIN/STAFF ONLY: Manually trigger a refund for an order.
        """
        if not request.user.is_staff:
            return Response({'error': 'Unauthorized. Staff only.'}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            order = self.get_object()
            
            if order.payment_status not in ['PAID', 'PARTIALLY_PAID']:
                 return Response({'error': 'Order is not in a refundable state'}, status=status.HTTP_400_BAD_REQUEST)
            
            amount_val = request.data.get('amount')
            amount = Decimal(str(amount_val)) if amount_val else order.total
            
            if amount > order.total:
                return Response({'error': 'Refund amount cannot exceed order total'}, status=status.HTTP_400_BAD_REQUEST)

            # Process Wallet Refund
            wallet, _ = Wallet.objects.get_or_create(user=order.user)
            wallet.balance += amount
            wallet.save()
            
            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type='CREDIT',
                amount=amount,
                source='REFUND',
                order=order,
                balance_after=wallet.balance,
                notes=request.data.get('notes', 'Manual refund by admin')
            )
            
            order.payment_status = 'REFUNDED'
            order.status = 'CANCELLED'
            order.save()
            
            # Notify Client
            async_to_sync(channel_layer.group_send)(
                f'notifications_{order.user.id}',
                {
                    'type': 'notification_message',
                    'message': {
                        'type': 'order_refunded',
                        'order_id': order.order_id,
                        'message': f'Your order {order.order_id} has been refunded (₹{amount})'
                    }
                }
            )
            
            return Response({'status': f'Refund of ₹{amount} processed successfully'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def invoice(self, request, *args, **kwargs):
        """Generate and download PDF invoice for an order"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER
            from django.http import HttpResponse
            from io import BytesIO
            import datetime
            
            order = self.get_object()
            
            # Only allow user to download their own invoice
            if order.user != request.user:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
            
            # Create PDF in memory
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
            
            # Container for PDF elements
            elements = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#DC2626'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            # Title
            elements.append(Paragraph("FOODIS", title_style))
            elements.append(Paragraph("Tax Invoice", styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            # Order Info
            order_info = [
                ['Invoice Number:', order.order_id],
                ['Order Date:', order.placed_at.strftime('%d %b %Y, %I:%M %p')],
                ['Payment Method:', order.payment_method],
                ['Payment Status:', order.payment_status],
            ]
            
            order_table = Table(order_info, colWidths=[2*inch, 3*inch])
            order_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ]))
            elements.append(order_table)
            elements.append(Spacer(1, 20))
            
            # Restaurant & Customer Info
            info_data = [
                ['From:', 'To:'],
                [order.restaurant.name if order.restaurant else 'N/A', order.user.name],
                [order.restaurant.address if order.restaurant else '', order.delivery_address],
                [order.restaurant.phone if order.restaurant else '', order.delivery_phone or order.user.phone],
            ]
            
            info_table = Table(info_data, colWidths=[3*inch, 3*inch])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 20))
            
            # Items Table
            items_data = [['Item', 'Qty', 'Price', 'Total']]
            for item in order.items.all():
                items_data.append([
                    item.menu_item.name if item.menu_item else 'Item',
                    str(item.quantity),
                    f'Rs.{item.price}',
                    f'Rs.{item.subtotal}'
                ])
            
            items_table = Table(items_data, colWidths=[3.5*inch, 0.7*inch, 1*inch, 1*inch])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DC2626')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(items_table)
            elements.append(Spacer(1, 20))
            
            # Totals
            totals_data = [
                ['Subtotal:', f'Rs.{order.subtotal}'],
                ['Delivery Fee:', f'Rs.{order.delivery_fee}'],
                ['Tax & Charges:', f'Rs.{order.tax}'],
                ['Discount:', f'-Rs.{order.discount}'],
                ['Grand Total:', f'Rs.{order.total}'],
            ]
            
            totals_table = Table(totals_data, colWidths=[4.5*inch, 1.7*inch])
            totals_table.setStyle(TableStyle([
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 12),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
                ('TOPPADDING', (0, -1), (-1, -1), 10),
            ]))
            elements.append(totals_table)
            elements.append(Spacer(1, 30))
            
            # Footer
            footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
            elements.append(Paragraph("Thank you for ordering with Foodis!", footer_style))
            elements.append(Paragraph(f"Generated on {datetime.datetime.now().strftime('%d %b %Y, %I:%M %p')}", footer_style))
            
            # Build PDF
            doc.build(elements)
            
            # Get PDF from buffer
            pdf = buffer.getvalue()
            buffer.close()
            
            # Return as downloadable file
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Invoice_{order.order_id}.pdf"'
            return response
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Invoice generation error: {error_details}")
            return Response({'error': str(e), 'details': error_details}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([AllowAny])
def search_restaurants(request):
    """AI-based restaurant and food search"""
    query = request.query_params.get('q', '')
    latitude = request.query_params.get('latitude')
    longitude = request.query_params.get('longitude')
    
    if not query:
        return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    radius = float(request.query_params.get('radius', 80))
    
    # Search restaurants
    restaurants_query = Restaurant.objects.filter(
        Q(name__icontains=query) | 
        Q(description__icontains=query) |
        Q(menu_items__name__icontains=query),
        status='APPROVED',
        is_active=True
    ).distinct()
    
    # Search menu items
    menu_items_query = MenuItem.objects.filter(
        Q(name__icontains=query),
        is_available=True,
        restaurant__status='APPROVED',
        restaurant__is_active=True
    )
    
    # Apply distance filtering if location available
    if latitude and longitude:
        try:
            user_location = (float(latitude), float(longitude))
            
            # Filter restaurants
            res_ids = []
            for r in restaurants_query:
                if distance(user_location, (float(r.latitude), float(r.longitude))).km <= radius:
                    res_ids.append(r.id)
            restaurants_query = restaurants_query.filter(id__in=res_ids)
            
            # Filter menu items (based on their restaurant's location)
            item_ids = []
            for item in menu_items_query:
                r = item.restaurant
                if distance(user_location, (float(r.latitude), float(r.longitude))).km <= radius:
                    item_ids.append(item.id)
            menu_items_query = menu_items_query.filter(id__in=item_ids)
        except (ValueError, TypeError):
            pass

    # Get AI recommendations if enabled
    if settings.AI_ENGINE_ENABLED:
        recommendations = get_recommendations(query, request.user if request.user.is_authenticated else None)
    else:
        recommendations = []
    
    restaurant_serializer = RestaurantSerializer(restaurants_query[:10], many=True, context={'request': request})
    menu_serializer = MenuItemSerializer(menu_items_query[:10], many=True)
    
    return Response({
        'restaurants': restaurant_serializer.data,
        'menu_items': menu_serializer.data,
        'recommendations': recommendations
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendations_view(request):
    """Get personalized recommendations"""
    recommendations = get_recommendations(None, request.user)
    return Response(recommendations, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_trending_view(request):
    """Get trending food items"""
    trending = get_trending_items()
    return Response(trending, status=status.HTTP_200_OK)


class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Coupons"""
    queryset = Coupon.objects.filter(is_active=True)
    serializer_class = CouponSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """Validate coupon code"""
        code = request.data.get('code')
        order_amount = Decimal(request.data.get('order_amount', 0))
        
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            serializer = CouponSerializer(coupon, context={'order_amount': order_amount})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Coupon.DoesNotExist:
            return Response({'error': 'Invalid coupon code'}, status=status.HTTP_404_NOT_FOUND)


class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Wallet"""
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def balance(self, request):
        """Get wallet balance"""
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for Reviews"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['restaurant', 'order']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # If restaurant ID is provided in query params, show all reviews for that restaurant
        # Otherwise, show reviews written by the current user
        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
            return Review.objects.filter(restaurant_id=restaurant_id)
        return Review.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Create or update review if already exists"""
        order_id = request.data.get('order')
        
        # Check if review already exists for this user and order
        existing_review = Review.objects.filter(
            user=request.user,
            order_id=order_id
        ).first()
        
        if existing_review:
            # Update existing review
            serializer = self.get_serializer(existing_review, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Create new review
            return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        review = serializer.save(user=self.request.user)
        # Update restaurant rating
        restaurant = review.restaurant
        res_data = Review.objects.filter(restaurant=restaurant).aggregate(
            avg=Avg('rating'), count=Count('id')
        )
        restaurant.rating = res_data['avg'] or 0
        restaurant.total_ratings = res_data['count'] or 0
        restaurant.save()
    
    def perform_update(self, serializer):
        review = serializer.save()
        # Update restaurant rating after edit
        restaurant = review.restaurant
        res_data = Review.objects.filter(restaurant=restaurant).aggregate(
            avg=Avg('rating'), count=Count('id')
        )
        restaurant.rating = res_data['avg'] or 0
        restaurant.total_ratings = res_data['count'] or 0
        restaurant.save()


class RiderReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for Rider Reviews"""
    serializer_class = RiderReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rider', 'order']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # If rider ID is provided, show all reviews for that rider
        # Otherwise, show reviews written by the current user
        rider_id = self.request.query_params.get('rider')
        if rider_id:
            return RiderReview.objects.filter(rider_id=rider_id)
        return RiderReview.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Create or update rider review if already exists"""
        order_id = request.data.get('order')
        
        # Check if review already exists for this order
        existing_review = RiderReview.objects.filter(
            order_id=order_id
        ).first()
        
        if existing_review:
            # Update existing review
            serializer = self.get_serializer(existing_review, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Create new review
            return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        review = serializer.save(user=self.request.user)
        # Update Rider Average Rating
        rider = review.rider
        profile = RiderProfile.objects.get(rider=rider)
        avg_rating = RiderReview.objects.filter(rider=rider).aggregate(Avg('rating'))['rating__avg']
        if avg_rating:
            profile.rating = round(Decimal(avg_rating), 2)
            profile.save()
    
    def perform_update(self, serializer):
        review = serializer.save()
        # Update Rider Average Rating after edit
        rider = review.rider
        profile = RiderProfile.objects.get(rider=rider)
        avg_rating = RiderReview.objects.filter(rider=rider).aggregate(Avg('rating'))['rating__avg']
        if avg_rating:
            profile.rating = round(Decimal(avg_rating), 2)
            profile.save()


class ProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for User Profile"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    
    def get_object(self):
        return self.request.user

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        # Add extra stats
        data = serializer.data
        data['total_orders'] = Order.objects.filter(user=request.user).count()
        data['total_spend'] = Order.objects.filter(user=request.user, payment_status='PAID').aggregate(total=Sum('total'))['total'] or 0
        return Response(data)


class AddressViewSet(viewsets.ModelViewSet):
    """ViewSet for Addresses"""
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SavedPaymentMethodViewSet(viewsets.ModelViewSet):
    """ViewSet for Saved Payment Methods"""
    serializer_class = SavedPaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SavedPaymentMethod.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavouriteRestaurantViewSet(viewsets.ModelViewSet):
    """ViewSet for Favourite Restaurants"""
    serializer_class = FavouriteRestaurantSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FavouriteRestaurant.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        restaurant_id = request.data.get('restaurant_id')
        fav, created = FavouriteRestaurant.objects.get_or_create(
            user=request.user, 
            restaurant_id=restaurant_id
        )
        if not created:
            fav.delete()
            return Response({'status': 'removed'}, status=status.HTTP_200_OK)
        return Response({'status': 'added'}, status=status.HTTP_201_CREATED)


class FavouriteMenuItemViewSet(viewsets.ModelViewSet):
    """ViewSet for Favourite Menu Items"""
    serializer_class = FavouriteMenuItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FavouriteMenuItem.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        menu_item_id = request.data.get('menu_item_id')
        fav, created = FavouriteMenuItem.objects.get_or_create(
            user=request.user, 
            menu_item_id=menu_item_id
        )
        if not created:
            fav.delete()
            return Response({'status': 'removed'}, status=status.HTTP_200_OK)
        return Response({'status': 'added'}, status=status.HTTP_201_CREATED)

