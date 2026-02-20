from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

import secrets
import string
from django.utils.text import slugify
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from django.contrib.auth import get_user_model
# [MODIFIED]: Consolidated duplicated imports from client.models into a single statement
from client.models import Restaurant, Order, Coupon, Wallet, WalletTransaction, Category, MenuItem, Review
from restaurant.models import RestaurantEarnings
from rider_legacy.models import RiderProfile, RiderEarnings, RiderBank
from .models import Banner, Commission, SitePolicy, SystemSettings
from .serializers import (
    UserSerializer, RestaurantSerializer, RiderProfileSerializer, OrderSerializer,
    BannerSerializer, CommissionSerializer, CouponSerializer, WalletTransactionSerializer,
    SitePolicySerializer, SystemSettingsSerializer, RestaurantEarningsSerializer, ReviewSerializer,
    MenuItemSerializer
)
from ai_engine.utils import get_admin_analytics, detect_fraud
import threading
from django.core.cache import cache
from ai_engine.image_generation import DishImageGenerator

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User Management"""
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    filterset_fields = ['role', 'is_active', 'is_verified']
    search_fields = ['phone', 'name', 'email']
    
    @action(detail=True, methods=['post'])
    def block_user(self, request, pk=None):
        """Block a user"""
        user = self.get_object()
        reason = request.data.get('reason', 'Admin action')
        
        user.is_active = False
        user.save()
        
        serializer = UserSerializer(user, context={'request': request})
        return Response({
            'message': f'User {user.name} blocked successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def unblock_user(self, request, pk=None):
        """Unblock a user"""
        user = self.get_object()
        
        user.is_active = True
        user.save()
        
        serializer = UserSerializer(user, context={'request': request})
        return Response({
            'message': f'User {user.name} unblocked successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        """Get comprehensive user details for Admin"""
        user = self.get_object()
        user_data = UserSerializer(user, context={'request': request}).data
        
        # Addresses
        from core.models import Address
        from core.serializers import AddressSerializer
        addresses = Address.objects.filter(user=user)
        
        # Wallet
        from client.models import Wallet
        try:
            wallet = Wallet.objects.get(user=user)
            wallet_balance = wallet.balance
        except Wallet.DoesNotExist:
            wallet_balance = 0.0
            
        # Recent Orders
        from client.models import Order
        from .serializers import OrderSerializer
        recent_orders = Order.objects.filter(user=user).order_by('-placed_at')[:5]

        # Wallet History
        from client.models import WalletTransaction
        from .serializers import WalletTransactionSerializer
        wallet_transactions = []
        try:
            if wallet:
                wallet_transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')[:5]
        except:
             pass
        
        return Response({
            'profile': user_data,
            'addresses': AddressSerializer(addresses, many=True, context={'request': request}).data,
            'wallet_balance': wallet_balance,
            'recent_orders': OrderSerializer(recent_orders, many=True, context={'request': request}).data,
            'wallet_transactions': WalletTransactionSerializer(wallet_transactions, many=True, context={'request': request}).data
        }, status=status.HTTP_200_OK)


class RestaurantViewSet(viewsets.ModelViewSet):
    """ViewSet for Restaurant Management"""
    serializer_class = RestaurantSerializer
    permission_classes = [IsAdminUser]
    queryset = Restaurant.objects.all().order_by('-created_at')
    filterset_fields = ['status', 'is_active', 'city']
    search_fields = ['name', 'owner__phone', 'city']
    ordering_fields = ['created_at', 'name', 'rating']
    ordering = ['-created_at']
    
    
    def create(self, request, *args, **kwargs):
        """Create restaurant with owner user account"""
        # [MODIFIED]: Inline imports safely moved to top of the file
        owner = None  # Track owner to clean up if restaurant creation fails
        
        try:
            # Extract owner details from request
            owner_name = request.data.get('create_owner_name', request.data.get('name', 'Restaurant Owner'))
            owner_phone = request.data.get('create_owner_phone', request.data.get('phone'))
            owner_email = request.data.get('create_owner_email', request.data.get('email', ''))
            
            # Validate owner phone
            if not owner_phone:
                return Response({'error': 'Owner phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Format phone number - add +91 prefix if only 10 digits
            if len(owner_phone) == 10 and owner_phone.isdigit():
                owner_phone = f'+91{owner_phone}'
            
            # Check if user with this phone already exists
            if User.objects.filter(phone=owner_phone).exists():
                return Response({'error': 'A user with this phone number already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate secure random password
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(12))
            
            # Create owner user account
            owner = User.objects.create_user(
                phone=owner_phone,
                name=owner_name,
                email=owner_email if owner_email else None,
                password=password,
                role='RESTAURANT',
                is_verified=True
            )
            
            # Generate unique slug for restaurant
            base_slug = slugify(request.data.get('name', 'restaurant'))
            slug = base_slug
            counter = 1
            while Restaurant.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            # Prepare restaurant data
            restaurant_data = request.data.copy()
            
            # Format restaurant phone number - add +91 prefix if only 10 digits
            restaurant_phone = restaurant_data.get('phone', '')
            if restaurant_phone and len(restaurant_phone) == 10 and restaurant_phone.isdigit():
                restaurant_data['phone'] = f'+91{restaurant_phone}'
            
            restaurant_data['owner'] = owner.id
            restaurant_data['slug'] = slug
            restaurant_data['status'] = 'PENDING'  # All admin-created restaurants start as PENDING
            restaurant_data['password_plain'] = password  # Store plain password for reference
            
            # Remove write-only fields that were used for owner creation
            restaurant_data.pop('create_owner_name', None)
            restaurant_data.pop('create_owner_phone', None)
            restaurant_data.pop('create_owner_email', None)
            
            # Create restaurant using serializer
            serializer = self.get_serializer(data=restaurant_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            # Add generated password to response
            response_data = serializer.data
            response_data['generated_password'] = password
            response_data['owner_phone'] = owner_phone
            
            headers = self.get_success_headers(serializer.data)
            return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
            
        except IntegrityError as e:
            # Clean up owner account if it was created
            if owner:
                owner.delete()
            
            error_msg = str(e)
            if 'phone' in error_msg.lower():
                return Response({'error': 'Phone number already exists'}, status=status.HTTP_400_BAD_REQUEST)
            elif 'email' in error_msg.lower():
                return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': f'Database constraint error: {error_msg}'}, status=status.HTTP_400_BAD_REQUEST)
                
        except ValidationError as e:
            # Clean up owner account if it was created
            if owner:
                owner.delete()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # Clean up owner account if it was created
            if owner:
                owner.delete()
            return Response({'error': f'Failed to create restaurant: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve restaurant"""
        restaurant = self.get_object()
        restaurant.status = 'APPROVED'
        restaurant.is_active = True
        restaurant.save()
        
        serializer = RestaurantSerializer(restaurant, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject restaurant"""
        restaurant = self.get_object()
        restaurant.status = 'REJECTED'
        restaurant.is_active = False
        restaurant.save()
        
        serializer = RestaurantSerializer(restaurant, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Suspend restaurant"""
        restaurant = self.get_object()
        restaurant.status = 'SUSPENDED'
        restaurant.is_active = False
        restaurant.save()
        
        serializer = RestaurantSerializer(restaurant, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'])
    def delete_restaurant(self, request, pk=None):
        """Permanently delete restaurant and its owner"""
        restaurant = self.get_object()
        restaurant_name = restaurant.name
        owner = restaurant.owner
        
        try:
            # Delete the restaurant (this will cascade delete related data)
            restaurant.delete()
            
            # Delete the owner user account if it exists
            if owner:
                owner.delete()
            
            return Response({
                'message': f'Restaurant "{restaurant_name}" and owner account deleted successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': f'Failed to delete restaurant: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class RiderProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for Rider Management"""
    serializer_class = RiderProfileSerializer
    permission_classes = [IsAdminUser]
    queryset = RiderProfile.objects.all()
    filterset_fields = ['status', 'is_online', 'vehicle_type']
    search_fields = ['rider__phone', 'rider__name', 'vehicle_number', 'license_number']
    
    def create(self, request, *args, **kwargs):
        """Create rider with user account, profile, and bank details"""
        # [MODIFIED]: Inline imports safely moved to top of the file
        rider_user = None  # Track user to clean up if creation fails
        
        try:
            # Extract rider details from request
            name = request.data.get('name')
            email = request.data.get('email', '')
            password = request.data.get('password')
            phone = request.data.get('phone')
            
            # Validate required fields
            if not name:
                return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not password:
                return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not phone:
                return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Format phone number - add +91 prefix if only 10 digits
            if len(phone) == 10 and phone.isdigit():
                phone = f'+91{phone}'
            
            # Check if user with this phone already exists
            if User.objects.filter(phone=phone).exists():
                return Response({'error': 'A user with this phone number already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create rider user account
            rider_user = User.objects.create_user(
                phone=phone,
                name=name,
                email=email if email else None,
                password=password,
                role='RIDER',
                is_verified=True
            )
            
            # Prepare rider profile data
            city = request.data.get('city', 'Himmatnagar')
            vehicle_number = request.data.get('vehicle_number', '')
            license_number = request.data.get('license_number', '')
            rider_status = request.data.get('status', 'APPROVED')
            
            # Create rider profile
            rider_profile = RiderProfile.objects.create(
                rider=rider_user,
                mobile_number=phone,
                city=city,
                vehicle_number=vehicle_number,
                license_number=license_number,
                status=rider_status,
                vehicle_type='BIKE'  # Default
            )
            
            # Create bank details if provided
            account_holder = request.data.get('account_holder_name', '')
            account_number = request.data.get('account_number', '')
            ifsc_code = request.data.get('ifsc_code', '')
            bank_name = request.data.get('bank_name', '')
            
            if account_holder and account_number and ifsc_code and bank_name:
                RiderBank.objects.create(
                    rider=rider_user,
                    account_holder_name=account_holder,
                    account_number=account_number,
                    ifsc_code=ifsc_code,
                    bank_name=bank_name,
                    verified=False
                )
            
            # Return response
            serializer = self.get_serializer(rider_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except IntegrityError as e:
            # Clean up rider user if it was created
            if rider_user:
                rider_user.delete()
            
            error_msg = str(e)
            if 'phone' in error_msg.lower():
                return Response({'error': 'Phone number already exists'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': f'Database constraint error: {error_msg}'}, status=status.HTTP_400_BAD_REQUEST)
                
        except ValidationError as e:
            # Clean up rider user if it was created
            if rider_user:
                rider_user.delete()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # Clean up rider user if it was created
            if rider_user:
                rider_user.delete()
            return Response({'error': f'Failed to create rider: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve rider"""
        profile = self.get_object()
        profile.status = 'APPROVED'
        profile.save()
        
        serializer = RiderProfileSerializer(profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject rider"""
        profile = self.get_object()
        profile.status = 'REJECTED'
        profile.save()
        
        serializer = RiderProfileSerializer(profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        """Block rider"""
        profile = self.get_object()
        profile.status = 'BLOCKED'
        profile.is_online = False
        profile.save()
        
        serializer = RiderProfileSerializer(profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Suspend rider"""
        profile = self.get_object()
        profile.status = 'SUSPENDED'
        profile.is_online = False
        profile.save()
        
        serializer = RiderProfileSerializer(profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)



class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Order Management"""
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    queryset = Order.objects.all()
    filterset_fields = ['status', 'payment_status', 'payment_method']
    search_fields = ['order_id', 'user__phone', 'restaurant__name']
    
    @action(detail=True, methods=['post'])
    def force_cancel(self, request, pk=None):
        """Force cancel an order (admin override)"""
        order = self.get_object()
        reason = request.data.get('reason', 'Admin cancelled')
        
        # Prevent cancelling delivered orders
        if order.status == 'DELIVERED':
            return Response({'error': 'Cannot cancel delivered orders'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'CANCELLED'
        order.save()
        
        # Refund if payment made
        if order.payment_status == 'PAID' and order.payment_method == 'WALLET':
            wallet = Wallet.objects.get(user=order.user)
            wallet.balance += order.total
            wallet.save()
            
            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type='CREDIT',
                amount=order.total,
                source='REFUND',
                description=f'Refund for cancelled order {order.order_id}: {reason}',
                order=order,
                balance_after=wallet.balance
            )
        
        serializer = OrderSerializer(order, context={'request': request})
        return Response({
            'message': 'Order cancelled successfully',
            'order': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Process refund for an order"""
        order = self.get_object()
        amount = Decimal(request.data.get('amount', order.total))
        reason = request.data.get('reason', 'Admin refund')
        
        if order.payment_status != 'PAID':
            return Response({'error': 'Order not paid'}, status=status.HTTP_400_BAD_REQUEST)
        
        if amount > order.total:
            return Response({'error': 'Refund amount exceeds order total'}, status=status.HTTP_400_BAD_REQUEST)
        
        wallet, _ = Wallet.objects.get_or_create(user=order.user)
        wallet.balance += amount
        wallet.save()
        
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='CREDIT',
            amount=amount,
            source='REFUND',
            description=f'Refund for order {order.order_id}: {reason}',
            order=order,
            balance_after=wallet.balance
        )
        
        return Response({
            'message': f'Refund of ₹{amount} processed successfully',
            'new_wallet_balance': float(wallet.balance)
        }, status=status.HTTP_200_OK)


class BannerViewSet(viewsets.ModelViewSet):
    """ViewSet for Banner Management"""
    serializer_class = BannerSerializer
    permission_classes = [IsAdminUser]
    queryset = Banner.objects.all()


class CommissionViewSet(viewsets.ModelViewSet):
    """ViewSet for Commission Management"""
    serializer_class = CommissionSerializer
    permission_classes = [IsAdminUser]
    queryset = Commission.objects.all()


class CouponViewSet(viewsets.ModelViewSet):
    """ViewSet for Coupon Management"""
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]
    queryset = Coupon.objects.all()


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category Management"""
    from client.serializers import CategorySerializer
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()


class SitePolicyViewSet(viewsets.ModelViewSet):
    """ViewSet for Site Policy Management"""
    serializer_class = SitePolicySerializer
    permission_classes = [IsAdminUser]
    queryset = SitePolicy.objects.all()
    lookup_field = 'slug'


class SystemSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for System Settings Management"""
    serializer_class = SystemSettingsSerializer
    permission_classes = [IsAdminUser]
    queryset = SystemSettings.objects.all()
    lookup_field = 'key'



class WalletTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Wallet Transaction Management"""
    serializer_class = WalletTransactionSerializer
    permission_classes = [IsAdminUser]
    queryset = WalletTransaction.objects.all()
    filterset_fields = ['transaction_type', 'source', 'wallet__user']
    search_fields = ['wallet__user__name', 'wallet__user__phone', 'description']



class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for Review Management"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminUser]
    queryset = Review.objects.all()
    filterset_fields = ['restaurant', 'rating']
    search_fields = ['restaurant__name', 'user__name', 'comment']


class RestaurantEarningsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Restaurant Earnings Management"""
    serializer_class = RestaurantEarningsSerializer
    permission_classes = [IsAdminUser]
    queryset = RestaurantEarnings.objects.all()
    filterset_fields = ['restaurant', 'date']
    search_fields = ['restaurant__name', 'order__order_id']


@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_stats(request):


    """Get admin dashboard statistics"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Users
    total_users = User.objects.count()
    clients = User.objects.filter(role='CLIENT').count()
    restaurants = User.objects.filter(role='RESTAURANT').count()
    riders = User.objects.filter(role='RIDER').count()
    
    # Restaurants
    pending_restaurants = Restaurant.objects.filter(status='PENDING').count()
    approved_restaurants = Restaurant.objects.filter(status='APPROVED').count()
    
    # Riders
    pending_riders = RiderProfile.objects.filter(status='UNDER_REVIEW').count()
    approved_riders = RiderProfile.objects.filter(status='APPROVED').count()
    
    # Orders
    total_orders = Order.objects.count()
    today_orders = Order.objects.filter(placed_at__date=today).count()
    week_orders = Order.objects.filter(placed_at__date__gte=week_ago).count()
    month_orders = Order.objects.filter(placed_at__date__gte=month_ago).count()
    
    # Revenue (Include PAID or DELIVERED)
    total_revenue = Order.objects.filter(
        Q(payment_status='PAID') | Q(status='DELIVERED')
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    today_revenue = Order.objects.filter(
        Q(payment_status='PAID') | Q(status='DELIVERED'),
        placed_at__date=today
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    week_revenue = Order.objects.filter(
        Q(payment_status='PAID') | Q(status='DELIVERED'),
        placed_at__date__gte=week_ago
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    # Commissions
    total_commissions = RestaurantEarnings.objects.aggregate(
        total=Sum('commission')
    )['total'] or Decimal('0.00')
    
    return Response({
        'users': {
            'total': total_users,
            'clients': clients,
            'restaurants': restaurants,
            'riders': riders
        },
        'restaurants': {
            'pending': pending_restaurants,
            'approved': approved_restaurants
        },
        'riders': {
            'pending': pending_riders,
            'approved': approved_riders
        },
        'orders': {
            'total': total_orders,
            'today': today_orders,
            'week': week_orders,
            'month': month_orders
        },
        'revenue': {
            'total': float(total_revenue),
            'today': float(today_revenue),
            'week': float(week_revenue)
        },
        'commissions': {
            'total': float(total_commissions)
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def revenue_graph(request):
    """Get revenue data for charts"""
    today = timezone.now().date()
    days = int(request.query_params.get('days', 30))
    
    # Generate date range
    date_list = [(today - timedelta(days=i)) for i in range(days-1, -1, -1)]
    
    daily_revenue = []
    for date in date_list:
        revenue = Order.objects.filter(
            Q(payment_status='PAID') | Q(status='DELIVERED'),
            placed_at__date=date
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        
        daily_revenue.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(revenue),
            'orders': Order.objects.filter(placed_at__date=date).count()
        })
    
    # Calculate growth
    current_period_revenue = sum(item['revenue'] for item in daily_revenue[-7:])
    previous_period_revenue = sum(item['revenue'] for item in daily_revenue[-14:-7]) if days >= 14 else 0
    
    growth_percentage = 0
    if previous_period_revenue > 0:
        growth_percentage = ((current_period_revenue - previous_period_revenue) / previous_period_revenue) * 100
    
    return Response({
        'daily_data': daily_revenue,
        'summary': {
            'total_revenue': sum(item['revenue'] for item in daily_revenue),
            'total_orders': sum(item['orders'] for item in daily_revenue),
            'average_order_value': sum(item['revenue'] for item in daily_revenue) / max(sum(item['orders'] for item in daily_revenue), 1),
            'growth_percentage': round(growth_percentage, 2)
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def analytics(request):
    """Get AI analytics"""
    analytics_data = get_admin_analytics()
    return Response(analytics_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def fraud_detection(request):
    """Get fraud detection results"""
    fraud_data = detect_fraud()
    return Response(fraud_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def adjust_wallet(request):
    """Adjust user wallet balance"""
    user_id = request.data.get('user_id')
    amount = Decimal(request.data.get('amount', 0))
    description = request.data.get('description', 'Admin Adjustment')
    
    try:
        user = User.objects.get(id=user_id)
        wallet, _ = Wallet.objects.get_or_create(user=user)
        
        if amount > 0:
            wallet.balance += amount
            transaction_type = 'CREDIT'
        else:
            wallet.balance += amount  # amount is negative
            transaction_type = 'DEBIT'
        
        wallet.save()
        
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type=transaction_type,
            amount=abs(amount),
            source='ADMIN',
            description=description,
            balance_after=wallet.balance
        )
        
        return Response({
            'message': 'Wallet adjusted successfully',
            'new_balance': float(wallet.balance)
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class MenuItemViewSet(viewsets.ModelViewSet):
    """ViewSet for Menu Item Management - All dishes from all restaurants"""
    pagination_class = None
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminUser]
    queryset = MenuItem.objects.select_related('restaurant', 'category').all()
    filterset_fields = ['restaurant', 'category', 'veg_type', 'is_available']
    search_fields = ['name', 'description', 'restaurant__name']
    ordering_fields = ['name', 'price', 'rating', 'total_orders', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['post'])
    def generate_images(self, request):
        """Trigger bulk image generation in background"""
        limit = int(request.data.get('limit', 20))
        source = request.data.get('source', 'stock')  # Default to stock photos
        
        # Validate source
        if source not in ['ai', 'stock']:
            return Response({'error': 'Invalid source. Choose "ai" or "stock"'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already running
        if cache.get('generation_in_progress'):
            return Response({'error': 'Generation already in progress'}, status=status.HTTP_400_BAD_REQUEST)
            
        def run_generation():
            cache.set('generation_in_progress', True, timeout=3600)
            cache.set('generation_status', {'status': 'Running', 'processed': 0, 'total': limit, 'source': source}, timeout=3600)
            
            try:
                # Select appropriate generator
                if source == 'ai':
                    generator = DishImageGenerator()
                else:
                    from ai_engine.stock_image_fetcher import StockImageFetcher
                    generator = StockImageFetcher()
                
                results = generator.process_batch(limit=limit)
                cache.set('generation_status', {'status': 'Completed', 'results': results, 'source': source}, timeout=3600)
            except Exception as e:
                cache.set('generation_status', {'status': 'Failed', 'error': str(e), 'source': source}, timeout=3600)
            finally:
                cache.delete('generation_in_progress')
        
        thread = threading.Thread(target=run_generation)
        thread.start()
        
        return Response({'message': 'Background generation started', 'limit': limit, 'source': source}, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=['get'])
    def generation_status(self, request):
        """Check status of background generation"""
        status_data = cache.get('generation_status', {'status': 'Idle'})
        return Response(status_data)


