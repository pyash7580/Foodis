from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Rider, OrderAssignment, Earning
from client.models import Order
from client.services.otp_service import OTPService

class AcceptOrderAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, order_id):
        try:
            rider = Rider.objects.get(email=request.user.email)
        except Rider.DoesNotExist:
            return Response({'error': 'Rider profile not found'}, status=status.HTTP_404_NOT_FOUND)

        if rider.status != 'ONLINE':
            return Response({'success': False, 'code': 'RIDER_NOT_ONLINE', 'message': 'You must be ONLINE to accept orders'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if rider already has an active assignment
        active_assignment = OrderAssignment.objects.filter(
            rider=rider,
            status__in=['ACCEPTED', 'PICKED_UP', 'ON_THE_WAY']
        ).exists()
        if active_assignment:
            return Response({'success': False, 'code': 'ALREADY_HAS_ACTIVE_ORDER', 'message': 'You already have an active mission'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Lock the order for atomic update
                order = Order.objects.select_for_update().get(
                    id=order_id,
                    status__in=['CONFIRMED', 'PREPARING', 'READY'],
                    rider__isnull=True
                )

                # Assign order to rider
                order.rider = request.user
                order.status = 'ASSIGNED'
                order.assigned_at = timezone.now()
                order.save()

                # Create assignment record
                assignment = OrderAssignment.objects.create(
                    rider=rider,
                    order_id=order.id,
                    status='ACCEPTED'
                )

                # Set rider to BUSY
                rider.status = 'BUSY'
                rider.save()

                return Response({
                    'success': True,
                    'message': f'Mission Accepted! Order #{order.order_id}',
                    'assignment_id': assignment.id
                })

        except Order.DoesNotExist:
            return Response({
                'success': False,
                'code': 'ORDER_ALREADY_ASSIGNED',
                'message': 'This order has been assigned to another rider or is no longer available'
            }, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PickupOrderAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, assignment_id):
        otp = request.data.get('otp')
        if not otp:
            return Response({'error': 'OTP is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assignment = OrderAssignment.objects.get(id=assignment_id, rider__email=request.user.email)
            order = Order.objects.get(id=assignment.order_id)
            
            if assignment.status != 'ACCEPTED':
                return Response({'error': 'Invalid status for pickup'}, status=status.HTTP_400_BAD_REQUEST)

            if OTPService.verify_otp(order, 'PICKUP', otp):
                assignment.status = 'PICKED_UP'
                assignment.save()

                order.status = 'PICKED_UP'
                order.picked_up_at = timezone.now()
                order.save()

                return Response({'success': True, 'message': 'Order picked up successfully'})
            
        except (OrderAssignment.DoesNotExist, Order.DoesNotExist):
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'success': False, 'code': 'INVALID_OTP', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Unexpected error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StartDeliveryAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, assignment_id):
        try:
            assignment = OrderAssignment.objects.get(id=assignment_id, rider__email=request.user.email)
            order = Order.objects.get(id=assignment.order_id)

            if assignment.status != 'PICKED_UP':
                return Response({'error': 'Order must be picked up first'}, status=status.HTTP_400_BAD_REQUEST)

            assignment.status = 'ON_THE_WAY'
            assignment.save()

            order.status = 'ON_THE_WAY'
            order.save()

            # Generate Delivery OTP
            OTPService.generate_otp(order, 'DELIVERY')
            
            return Response({'success': True, 'message': 'Started delivery successfully'})

        except (OrderAssignment.DoesNotExist, Order.DoesNotExist):
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

class CompleteOrderAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, assignment_id):
        otp = request.data.get('otp')
        if not otp:
            return Response({'error': 'OTP is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                assignment = OrderAssignment.objects.select_for_update().get(id=assignment_id, rider__email=request.user.email)
                order = Order.objects.select_for_update().get(id=assignment.order_id)
                rider = Rider.objects.get(email=request.user.email)

                if assignment.status != 'ON_THE_WAY':
                    return Response({'error': 'Invalid status for completion'}, status=status.HTTP_400_BAD_REQUEST)

                if OTPService.verify_otp(order, 'DELIVERY', otp):
                    assignment.status = 'DELIVERED'
                    assignment.save()

                    order.status = 'DELIVERED'
                    order.delivered_at = timezone.now()
                    order.payment_status = 'PAID'
                    order.save()

                    # Add earnings
                    earning_amount = Decimal('40.00') # Fixed decimal mismatch
                    rider.wallet_balance += earning_amount
                    rider.status = 'ONLINE' # Back to Online after delivery
                    rider.save()

                    Earning.objects.create(
                        rider=rider,
                        order_id=order.id,
                        amount=earning_amount,
                        transaction_type='DELIVERY'
                    )

                    return Response({'success': True, 'message': f'Order delivered! Rs.{earning_amount} added to wallet.'})

        except (OrderAssignment.DoesNotExist, Order.DoesNotExist):
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'success': False, 'code': 'INVALID_OTP', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Unexpected error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FailDeliveryAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, assignment_id):
        reason = request.data.get('reason', 'Unknown reason')
        try:
            assignment = OrderAssignment.objects.get(id=assignment_id, rider__email=request.user.email)
            order = Order.objects.get(id=assignment.order_id)
            rider = Rider.objects.get(email=request.user.email)

            assignment.status = 'REJECTED' # Reuse for failure
            assignment.save()

            order.status = 'CANCELLED'
            order.save()

            rider.status = 'ONLINE'
            rider.save()

            return Response({'success': True, 'message': f'Delivery failed marked: {reason}'})
            
        except (OrderAssignment.DoesNotExist, Order.DoesNotExist):
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
