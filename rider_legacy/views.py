from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from geopy.distance import distance
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .serializers import (
    RiderProfileSerializer, RiderLocationSerializer, OrderSerializer, 
    RiderEarningsSerializer, RiderReviewSerializer, RiderDocumentSerializer, 
    RiderBankSerializer, RiderNotificationSerializer, IncentiveSchemeSerializer,
    RiderIncentiveProgressSerializer
)
from .models import (
    RiderProfile, RiderEarnings, RiderLocation, RiderReview, 
    RiderDocument, RiderBank, RiderNotification, IncentiveScheme,
    RiderIncentiveProgress
)
from core.utils import generate_otp, broadcast_order_status, broadcast_order_location
from client.models import Order
from ai_engine.utils import calculate_rider_efficiency

channel_layer = get_channel_layer()


class RiderProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for Rider Profile"""
    serializer_class = RiderProfileSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        # In production/demo, allow seeing ALL riders for visibility
        if self.action == 'list':
            return RiderProfile.objects.all()
        return RiderProfile.objects.filter(rider=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(rider=self.request.user, status='PENDING')
    
    @action(detail=True, methods=['post'])
    def toggle_online(self, request, pk=None):
        """Toggle online/offline status"""
        profile = self.get_object()
        profile.is_online = not profile.is_online
        profile.save()
        serializer = RiderProfileSerializer(profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        """Update rider location"""
        profile = self.get_object()
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        if not latitude or not longitude:
            return Response({'error': 'Latitude and longitude are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        profile.current_latitude = latitude
        profile.current_longitude = longitude
        profile.save()
        
        # Store location history
        RiderLocation.objects.create(
            rider=request.user,
            latitude=latitude,
            longitude=longitude
        )
        
        # Update order location if rider has active order
        active_order = Order.objects.filter(
            rider=request.user,
            status__in=['ASSIGNED', 'PICKED_UP', 'ON_THE_WAY']
        ).first()
        
        if active_order:
            active_order.rider_latitude = latitude
            active_order.rider_longitude = longitude
            active_order.save()
            
            # Send location update to client
            broadcast_order_location(active_order.order_id, latitude, longitude)
        
        serializer = RiderProfileSerializer(profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get rider statistics"""
        profile = self.get_object()
        
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Deliveries
        total_deliveries = Order.objects.filter(rider=request.user, status='DELIVERED').count()
        today_deliveries = Order.objects.filter(
            rider=request.user, status='DELIVERED', delivered_at__date=today
        ).count()
        week_deliveries = Order.objects.filter(
            rider=request.user, status='DELIVERED', delivered_at__date__gte=week_ago
        ).count()
        
        # Earnings
        total_earnings = RiderEarnings.objects.filter(rider=request.user).aggregate(
            total=Sum('total_earning')
        )['total'] or Decimal('0.00')
        
        today_earnings = RiderEarnings.objects.filter(
            rider=request.user, date=today
        ).aggregate(total=Sum('total_earning'))['total'] or Decimal('0.00')
        
        week_earnings = RiderEarnings.objects.filter(
            rider=request.user, date__gte=week_ago
        ).aggregate(total=Sum('total_earning'))['total'] or Decimal('0.00')
        
        # Active orders
        active_orders = Order.objects.filter(
            rider=request.user,
            status__in=['ASSIGNED', 'PICKED_UP', 'ON_THE_WAY']
        ).count()
        
        # Efficiency score
        efficiency = calculate_rider_efficiency(request.user)
        
        return Response({
            'deliveries': {
                'total': total_deliveries,
                'today': today_deliveries,
                'week': week_deliveries
            },
            'earnings': {
                'total': float(total_earnings),
                'today': float(today_earnings),
                'week': float(week_earnings)
            },
            'active_orders': active_orders,
            'efficiency_score': efficiency
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get full dashboard state"""
        profile, created = RiderProfile.objects.get_or_create(rider=request.user)
        
        # Get Stats
        today = timezone.now().date()
        today_earnings = RiderEarnings.objects.filter(
            rider=request.user, date=today
        ).aggregate(total=Sum('total_earning'))['total'] or Decimal('0.00')
        
        today_deliveries = Order.objects.filter(
            rider=request.user, status='DELIVERED', delivered_at__date=today
        ).count()
        
        # Get Active Order
        active_order_data = None
        if profile.current_order:
            active_order_data = OrderSerializer(profile.current_order, context={'request': request}).data
            
        # Get ALL Active Orders (Stacking Support)
        active_orders = Order.objects.filter(
            rider=request.user,
            status__in=['ASSIGNED', 'PICKED_UP', 'ON_THE_WAY']
        )
        active_orders_data = OrderSerializer(active_orders, many=True, context={'request': request}).data
            
        # Get Bank Details
        bank_details = None
        try:
            bank = RiderBank.objects.get(rider=request.user)
            bank_details = {
                'account_holder_name': bank.account_holder_name,
                'account_number': bank.account_number,
                'ifsc_code': bank.ifsc_code,
                'bank_name': bank.bank_name,
                'verified': bank.verified
            }
        except RiderBank.DoesNotExist:
            pass
        
        return Response({
            'profile': {
                'id': profile.id,
                'name': request.user.name,
                'phone': request.user.phone,
                'mobile_number': profile.mobile_number,
                'status': profile.status,
                'is_online': profile.is_online,
                'city': profile.city,
                'rating': float(profile.rating),
                'total_deliveries': profile.total_deliveries,
                'wallet_balance': float(profile.wallet_balance),
                'vehicle_number': profile.vehicle_number,
                'vehicle_type': profile.vehicle_type,
                'license_number': profile.license_number,
                'profile_photo': str(profile.profile_photo) if profile.profile_photo else None,
                'bank_details': bank_details
            },
            'stats': {
                'today_earnings': float(today_earnings),
                'today_deliveries': today_deliveries,
                'wallet_balance': float(profile.wallet_balance),
                'total_deliveries': profile.total_deliveries,
                'rating': float(profile.rating)
            },
            'active_order': active_order_data,
            'active_orders': active_orders_data  # New Field
        })




class RiderNotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for Rider Notifications"""
    serializer_class = RiderNotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RiderNotification.objects.filter(rider=self.request.user)
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        RiderNotification.objects.filter(rider=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'All notifications marked as read'})

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'Notification marked as read'})


class IncentiveViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Incentive Schemes and Progress"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'progress':
            return RiderIncentiveProgressSerializer
        return IncentiveSchemeSerializer
        
    def get_queryset(self):
        return IncentiveScheme.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def progress(self, request):
        """Get rider progress for all active incentives"""
        today = timezone.now().date()
        # Ensure progress records exist for active schemes
        active_schemes = IncentiveScheme.objects.filter(is_active=True)
        for scheme in active_schemes:
            RiderIncentiveProgress.objects.get_or_create(
                rider=request.user, 
                scheme=scheme, 
                date=today
            )
            
        progress = RiderIncentiveProgress.objects.filter(rider=request.user, date=today)
        serializer = RiderIncentiveProgressSerializer(progress, many=True)
        return Response(serializer.data)


class RiderOnboardingViewSet(viewsets.GenericViewSet):

    """ViewSet for Rider Onboarding Process"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def update_personal(self, request):
        """Step 1: Update Personal Details (Name, Email)"""
        profile, created = RiderProfile.objects.get_or_create(rider=request.user)
        user = request.user
        
        # Update User model for Name/Email
        if 'name' in request.data:
            user.name = request.data['name']
        if 'email' in request.data:
            user.email = request.data['email']
        user.save()
        
        # Update Profile if needed (e.g. city is sent here or next step)
        # For this step, we just confirm personal details are set
        if profile.onboarding_step < 1:
            profile.onboarding_step = 1
            profile.save()
            
        return Response({'status': 'Personal details updated', 'step': 1})

    @action(detail=False, methods=['post'])
    def update_city(self, request):
        """Step 2: Update City"""
        profile, created = RiderProfile.objects.get_or_create(rider=request.user)
        city = request.data.get('city')
        
        if not city:
            return Response({'error': 'City is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        profile.city = city
        if profile.onboarding_step < 2:
            profile.onboarding_step = 2
        profile.save()
        return Response({'status': 'City updated', 'step': 2})

    @action(detail=False, methods=['post'])
    def update_vehicle(self, request):
        """Step 3: Update Vehicle Details"""
        profile, created = RiderProfile.objects.get_or_create(rider=request.user)
        serializer = RiderProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            profile = serializer.save()
            if profile.onboarding_step < 3:
                profile.onboarding_step = 3
                profile.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def upload_document(self, request):
        """Step 4: Upload Documents"""
        # data needs: document_type, file
        serializer = RiderDocumentSerializer(data=request.data)
        if serializer.is_valid():
            doc = serializer.save(rider=request.user)
            profile = RiderProfile.objects.get(rider=request.user)
            # We don't auto-advance step here on single upload, client should call 'next' or we check count
            # For simplicity, if they upload at least one, we allow them to proceed in UI
            if profile.onboarding_step < 4:
                profile.onboarding_step = 4
                profile.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def update_bank(self, request):
        """Step 5: Update Bank Details"""
        bank, created = RiderBank.objects.get_or_create(rider=request.user)
        serializer = RiderBankSerializer(bank, data=request.data, partial=True)
        if serializer.is_valid():
            bank = serializer.save()
            profile = RiderProfile.objects.get(rider=request.user)
            if profile.onboarding_step < 5:
                profile.onboarding_step = 5
                profile.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'])
    def submit(self, request):
        """Final Submission (Step 6)"""
        profile = RiderProfile.objects.get(rider=request.user)
        
        if profile.status in ['APPROVED', 'SUSPENDED', 'BLOCKED']:
             return Response({'status': 'Already processed', 'current_status': profile.status}, status=status.HTTP_200_OK)

        profile.status = 'UNDER_REVIEW'
        profile.onboarding_step = 6
        profile.is_onboarding_complete = True
        profile.save()
        return Response({'status': 'Submitted for verification', 'redirect': 'status'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rider_login_status(request):
    """API for strict redirection logic"""
    try:
        profile = RiderProfile.objects.get(rider=request.user)
        
        if profile.status == 'BLOCKED':
            return Response({"redirect": "blocked"})
            
        if profile.status == 'APPROVED' and profile.is_onboarding_complete:
            return Response({"redirect": "dashboard"})
        elif profile.status == 'UNDER_REVIEW':
            return Response({"redirect": "status", "state": "UNDER_REVIEW"})
        elif profile.status == 'REJECTED':
            return Response({"redirect": "rejected"})
        else:
            return Response({
                "redirect": "onboarding",
                "step": profile.onboarding_step
            })
    except RiderProfile.DoesNotExist:
        # Avoid crash if phone is null or other profiling issues
        profile, created = RiderProfile.objects.get_or_create(
            rider=request.user,
            defaults={
                'mobile_number': request.user.phone,
                'status': 'NEW',
                'onboarding_step': 0
            }
        )
        return Response({
            "redirect": "onboarding",
            "step": 0
        })
    except Exception as e:
        # Fallback for any other errors (database, etc)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Rider Orders"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(
            Q(rider=self.request.user) | 
            Q(status__in=['CONFIRMED', 'PREPARING', 'READY'], rider__isnull=True)
        )
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available orders for assignment"""
        profile = RiderProfile.objects.filter(rider=request.user, is_online=True).first()
        
        if not profile or profile.status != 'APPROVED':
            return Response({'error': 'Rider not available or offline'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        from django.db.models import Q
        
        # 📌 City-Wise Filtering: Get orders ready for pickup or preparing in the SAME CITY
        city_filters = Q()
        if profile.city_id:
            city_filters |= Q(city_id=profile.city_id)
            city_filters |= Q(restaurant__city_id=profile.city_id)
            
        if profile.city:
            city_filters |= Q(restaurant__city__iexact=profile.city)
            
        if not city_filters:
            return Response([], status=status.HTTP_200_OK)

        available_orders = Order.objects.filter(
            city_filters,
            status__in=['CONFIRMED', 'PREPARING', 'READY'],
            rider__isnull=True
        ).select_related('restaurant')
        
        # Calculate distances & format consistent output
        nearby_orders = []
        rider_location = None
        if profile.current_latitude and profile.current_longitude:
            rider_location = (float(profile.current_latitude), float(profile.current_longitude))
            
        for order in available_orders:
            try:
                dist = None
                delivery_dist = None
                estimated_earning = 40.0
                
                if rider_location and order.restaurant.latitude and order.restaurant.longitude:
                    try:
                        restaurant_location = (float(order.restaurant.latitude), float(order.restaurant.longitude))
                        dist = distance(rider_location, restaurant_location).km
                    except Exception as e:
                        print(f"Error calculating restaurant dist {order.id}: {e}")
                        
                    try:
                        if order.delivery_latitude and order.delivery_longitude:
                            delivery_location = (float(order.delivery_latitude), float(order.delivery_longitude))
                            delivery_dist = distance(restaurant_location, delivery_location).km
                    except Exception as e:
                        print(f"Error calculating delivery dist {order.id}: {e}")
                    
                    # Only show orders within reasonable pickup range (e.g., 20km)
                    if dist is not None and dist > 20:
                        continue
                        
                    estimated_earning = 40 + (dist * 5 if dist else 0) + ((delivery_dist or 0) * 10)
                
                nearby_orders.append({
                    'order': OrderSerializer(order, context={'request': request}).data,
                    'distance': round(dist, 2) if dist is not None else None,
                    'delivery_distance': round(delivery_dist, 2) if delivery_dist is not None else None,
                    'estimated_earning': round(estimated_earning, 2)
                })
            except Exception as e:
                print(f"Error processing order {order.id}: {e}")
                continue
        
        # Sort by proximity to rider
        nearby_orders.sort(key=lambda x: x['distance'] if x['distance'] is not None else float('inf'))
        return Response(nearby_orders, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get current active order"""
        profile = RiderProfile.objects.filter(rider=request.user).first()
        if not profile:
             return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get active order from profile or query
        active_order = profile.current_order
        
        # Fallback query if profile.current_order is desync
        if not active_order:
             active_order = Order.objects.filter(
                rider=request.user,
                status__in=['ASSIGNED', 'PICKED_UP', 'ON_THE_WAY']
            ).first()
        
        if active_order:
            serializer = OrderSerializer(active_order, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(None, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get past orders (DELIVERED, CANCELLED, REJECTED)"""
        # Parse query params for simple filtering if needed
        status_filter = request.query_params.get('status')
        days = request.query_params.get('days', 30)
        
        start_date = timezone.now() - timedelta(days=int(days))
        
        queryset = Order.objects.filter(
            rider=request.user,
            placed_at__gte=start_date
        ).exclude(
            status__in=['ASSIGNED', 'PICKED_UP', 'ON_THE_WAY', 'CONFIRMED', 'PREPARING', 'READY']
        ).order_by('-placed_at')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject/Hide an available order"""
        # For now, just a placeholder to log or handle client-side hiding.
        # Ideally, we should suggest this order less frequently or mark as rejected for this rider.
        return Response({'status': 'Order rejected locally'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept order assignment"""
        order = self.get_object()
        profile = RiderProfile.objects.filter(rider=request.user).first()
        
        if not profile or not profile.is_online:
            return Response({'error': 'Rider not available'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # 📌 RELAXED CHECK: ALLOW ORDER STACKING (Multiple Active Orders)
        # if profile.current_order:
        #     return Response({'error': 'You already have an active order'}, 
        #                   status=status.HTTP_400_BAD_REQUEST)

        # Check validity
        if order.status not in ['CONFIRMED', 'PREPARING', 'READY'] or order.rider:
            return Response({'error': 'Order not available'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Assign Order
        order.rider = request.user
        order.status = 'ASSIGNED'
        # 🚫 REMOVED: order.pickup_otp = generate_otp()
        # The OTP is now generated by the Restaurant on Acceptance for consistency.
        order.save()
        
        # Update Profile State
        profile.current_order = order
        profile.save()
        
        # Send notification to restaurant and client
        # Send notification to restaurant owner (using NotificationConsumer pattern)
        async_to_sync(channel_layer.group_send)(
            f'notifications_{order.restaurant.owner.id}',
            {
                'type': 'notification_message',
                'message': {
                    'type': 'order_assigned',
                    'order_id': order.order_id,
                    'rider_name': request.user.name,
                    'message': f'Rider {request.user.name} has been assigned to order {order.order_id}'
                }
            }
        )
        
        async_to_sync(channel_layer.group_send)(
            f'notifications_{order.user.id}',
            {
                'type': 'notification_message',
                'message': {
                    'type': 'rider_assigned',
                    'order_id': order.order_id,
                    'message': f'Rider {request.user.name} has been assigned to your order'
                }
            }
        )
        
        # Broadcast status change
        broadcast_order_status(order)
        
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def arrived_at_restaurant(self, request, pk=None):
        """Rider arrived at restaurant"""
        order = self.get_object()
        if order.rider != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
            
        allowed_statuses = ['ASSIGNED', 'PREPARING', 'READY', 'CONFIRMED']
        if order.status not in allowed_statuses:
             return Response({'error': f'Invalid order status: {order.status}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # We don't have a specific 'ARRIVED_AT_RESTAURANT' status in Order model yet, 
        # but we can log it or broadcast it. For now, let's keep it simple.
        # order.status = 'ARRIVED' # If we added this to choices
        # For Zomato-like feel, we just update the UI state.
        return Response({'status': 'Arrived at restaurant updated'})

    
    @action(detail=True, methods=['post'])
    def pickup(self, request, pk=None):
        """Confirm pickup with OTP"""
        order = self.get_object()
        otp = request.data.get('otp')
        
        if order.rider != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        if order.status not in ['ASSIGNED', 'READY']:
            return Response({'error': f'Invalid order status: {order.status}'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if not otp:
            return Response({'error': 'OTP required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify Restaurant OTP
        from client.services.otp_service import OTPService
        from rest_framework.exceptions import ValidationError
        
        is_valid = False
        error_detail = "Invalid OTP"
        
        # PRIORITY 1: Check legacy pickup_otp field first (for backward compatibility)
        if order.pickup_otp and str(otp).strip() == str(order.pickup_otp).strip():
            is_valid = True
            print(f"[SUCCESS] OTP verified via legacy pickup_otp field for order {order.order_id}")
        else:
            # PRIORITY 2: Try secure verification via OTPService (for new orders)
            try:
                is_valid = OTPService.verify_otp(order, 'PICKUP', otp, user=request.user)
                print(f"[SUCCESS] OTP verified via OTPService for order {order.order_id}")
            except ValidationError as e:
                error_detail = str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)
                print(f"[FAILED] Both legacy and OTPService verification failed. Error: {error_detail}")
            except Exception as e:
                error_detail = str(e)
                print(f"[ERROR] Unexpected error during OTP verification: {error_detail}")
        
        if not is_valid:
            return Response({'error': error_detail}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'PICKED_UP'
        order.picked_up_at = timezone.now()
        
        # Generate Delivery OTP for Customer
        order.delivery_otp = generate_otp()
        order.save()
        
        # Send notification to client
        async_to_sync(channel_layer.group_send)(
            f'notifications_{order.user.id}',
            {
                'type': 'notification_message',
                'message': {
                    'type': 'order_picked_up',
                    'order_id': order.order_id,
                    'message': f'Your order {order.order_id} has been picked up'
                }
            }
        )
        
        # Broadcast status change
        broadcast_order_status(order)
        
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def start_delivery(self, request, pk=None):
        """Start delivery"""
        order = self.get_object()
        
        if order.rider != request.user or order.status != 'PICKED_UP':
            return Response({'error': 'Invalid order status'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'ON_THE_WAY'
        order.save()
        
        # Broadcast status change
        broadcast_order_status(order)
        
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def arrived_at_customer(self, request, pk=None):
        """Rider arrived at customer location"""
        order = self.get_object()
        if order.rider != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        if order.rider != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        allowed_statuses = ['PICKED_UP', 'ON_THE_WAY']
        if order.status not in allowed_statuses:
             return Response({'error': f'Invalid order status: {order.status}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Optional: Auto-transition to ON_THE_WAY if still in PICKED_UP to reflect progress?
        # For now, just allowing the action is safer.
        return Response({'status': 'Arrived at customer location updated'}, status=status.HTTP_200_OK)

    
    @action(detail=True, methods=['post'])
    def deliver(self, request, pk=None):
        """Confirm delivery with OTP"""
        order = self.get_object()
        otp = request.data.get('otp')
        
        if order.rider != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        if order.status not in ['PICKED_UP', 'ON_THE_WAY']:
            return Response({'error': f'Invalid order status: {order.status}'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if not otp:
            return Response({'error': 'OTP required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify Customer OTP
        if order.delivery_otp and str(otp).strip() != str(order.delivery_otp).strip():
            return Response({'error': 'Invalid OTP. Please check with customer.'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'DELIVERED'
        order.delivered_at = timezone.now()
        
        # Mark as PAID upon successful delivery (important for earnings signal)
        order.payment_status = 'PAID'
            
        order.save()
        
        # Create rider earning
        # Logic: 10% of order value, min ₹30.00
        delivery_fee = max(Decimal('30.00'), order.total * Decimal('0.10'))
        
        RiderEarnings.objects.create(
            rider=request.user,
            order=order,
            delivery_fee=delivery_fee,
            total_earning=delivery_fee,
            date=timezone.now().date()
        )
        
        # Update rider stats & Clear active order
        profile = RiderProfile.objects.get(rider=request.user)
        profile.total_deliveries += 1
        profile.current_order = None # 📌 CLEAR ACTIVE ORDER
        profile.save()
        
        # 🎊 INCENTIVE LOGIC
        today = timezone.now().date()
        progress_records = RiderIncentiveProgress.objects.filter(rider=request.user, date=today, is_completed=False)
        for progress in progress_records:
            progress.current_count += 1
            if progress.current_count >= progress.scheme.target_count:
                progress.is_completed = True
                progress.earned_at = timezone.now()
                # Update wallet with reward
                profile.wallet_balance += progress.scheme.reward_amount
                profile.save()
                
                # Notify rider
                RiderNotification.objects.create(
                    rider=request.user,
                    title="Incentive Earned! 🎊",
                    message=f"Congratulations! You completed '{progress.scheme.title}' and earned ₹{progress.scheme.reward_amount}",
                    notification_type='INCENTIVE'
                )
            progress.save()

        
        # Send notification to client and restaurant
        async_to_sync(channel_layer.group_send)(
            f'notifications_{order.user.id}',
            {
                'type': 'notification_message',
                'message': {
                    'type': 'order_delivered',
                    'order_id': order.order_id,
                    'message': f'Your order {order.order_id} has been delivered'
                }
            }
        )
        
        # Broadcast status change
        broadcast_order_status(order)
        
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class RiderEarningsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Rider Earnings"""
    serializer_class = RiderEarningsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RiderEarnings.objects.filter(rider=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get earnings summary"""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        today_earnings = RiderEarnings.objects.filter(
            rider=request.user, date=today
        ).aggregate(total=Sum('total_earning'))['total'] or Decimal('0.00')
        
        week_earnings = RiderEarnings.objects.filter(
            rider=request.user, date__gte=week_ago
        ).aggregate(total=Sum('total_earning'))['total'] or Decimal('0.00')
        
        month_earnings = RiderEarnings.objects.filter(
            rider=request.user, date__gte=month_ago
        ).aggregate(total=Sum('total_earning'))['total'] or Decimal('0.00')
        
        return Response({
            'today': float(today_earnings),
            'week': float(week_earnings),
            'month': float(month_earnings)
        }, status=status.HTTP_200_OK)


class RiderReviewViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Rider Reviews"""
    serializer_class = RiderReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RiderReview.objects.filter(rider=self.request.user)

