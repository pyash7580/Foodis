from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.utils.decorators import method_decorator
from .models import Rider, OrderAssignment, Earning, Payout
from .decorators import rider_required
import random
from client.models import Order
from core.utils import generate_otp
from client.services.otp_service import OTPService
from rest_framework.exceptions import ValidationError

class LoginView(View):
    # ... (LoginView logic is fine, but I'll update the imports above)
    template_name = 'rider/auth/login.html'

    def get(self, request):
        if 'rider_phone' in request.session:
            return redirect('rider:dashboard')
        return render(request, self.template_name)

    def post(self, request):
        phone = request.POST.get('phone')
        city = request.POST.get('city', 'Mehsana')
        if not phone:
            messages.error(request, "Please enter your mobile number")
            return render(request, self.template_name)

        otp_code = str(random.randint(100000, 999999))
        request.session['pending_phone'] = phone
        request.session['pending_otp'] = otp_code
        request.session['pending_city'] = city
        
        messages.success(request, f"OTP sent (Simulation: {otp_code})")
        return redirect('rider:verify_otp')

class VerifyOTPView(View):
    template_name = 'rider/auth/verify.html'

    def get(self, request):
        phone = request.session.get('pending_phone')
        if not phone:
            return redirect('rider:login')
        return render(request, self.template_name, {'phone': phone})

    def post(self, request):
        phone = request.session.get('pending_phone')
        city = request.session.get('pending_city', 'Mehsana')
        otp_input = request.POST.get('otp')
        stored_otp = request.session.get('pending_otp')

        if not phone or not stored_otp:
            return redirect('rider:login')

        if otp_input == stored_otp:
            # Create or get rider with the chosen city
            rider, created = Rider.objects.get_or_create(
                phone=phone,
                defaults={'full_name': f'Rider {phone[-4:]}', 'city': city}
            )
            
            # If rider exists, ensure their city is updated to the one selected
            if not created:
                rider.city = city
                rider.save()

            request.session['rider_phone'] = phone
            # Clean up session
            for key in ['pending_phone', 'pending_otp', 'pending_city']:
                if key in request.session:
                    del request.session[key]
            
            return redirect('rider:dashboard')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, self.template_name, {'phone': phone})

class LogoutView(View):
    def get(self, request):
        if 'rider_phone' in request.session:
            del request.session['rider_phone']
        return redirect('rider:login')

class DashboardView(View):
    template_name = 'rider/dashboard/home.html'

    @method_decorator(rider_required)
    def get(self, request):
        phone = request.session['rider_phone']
        rider = Rider.objects.get(phone=phone)
        
        # Check for active assignment
        active_assignment = OrderAssignment.objects.filter(
            rider=rider, 
            status__in=['ACCEPTED', 'PICKED_UP', 'ON_THE_WAY']
        ).first()
        
        # Check for new ping (Specifically assigned)
        ping_assignment = None
        if not active_assignment:
            ping_assignment = OrderAssignment.objects.filter(
                rider=rider, 
                status='ASSIGNED'
            ).first()
            
        # Check for Available Orders in the same city (Broadcasted)
        available_pings = []
        if not active_assignment and rider.is_online:
            # Exclude orders already accepted by ANYONE
            accepted_order_ids = OrderAssignment.objects.filter(
                status__in=['ACCEPTED', 'PICKED_UP', 'ON_THE_WAY']
            ).values_list('order_id', flat=True)
            
            # Fetch orders in same city that are eligible for pickup
            # Statuses: CONFIRMED, PREPARING, READY
            available_pings = Order.objects.filter(
                restaurant__city__iexact=rider.city,
                status__in=['CONFIRMED', 'PREPARING', 'READY'],
                rider__isnull=True
            ).exclude(id__in=accepted_order_ids).order_by('-placed_at')

        return render(request, self.template_name, {
            'rider': rider,
            'active_assignment': active_assignment,
            'ping_assignment': ping_assignment,
            'available_pings': available_pings
        })

class OrderActionView(View):
    @method_decorator(rider_required)
    def post(self, request, assignment_id):
        action = request.POST.get('action')
        phone = request.session['rider_phone']
        rider = Rider.objects.get(phone=phone)
        
        try:
            assignment = OrderAssignment.objects.get(id=assignment_id, rider=rider)
        except OrderAssignment.DoesNotExist:
            messages.error(request, "Task not found")
            return redirect('rider:dashboard')

        if action == 'ACCEPT':
            has_active = OrderAssignment.objects.filter(
                rider=rider, 
                status__in=['ACCEPTED', 'PICKED_UP', 'ON_THE_WAY']
            ).exists()
            if has_active:
                messages.error(request, "You already have an active order")
            else:
                assignment.status = 'ACCEPTED'
                assignment.save()
                
                messages.success(request, "Order Accepted!")

        elif action == 'REJECT':
            assignment.status = 'REJECTED'
            assignment.save()
            messages.info(request, "Order Rejected")

        elif action == 'PICKUP':
            otp_input = request.POST.get('otp')
            if not otp_input:
                messages.error(request, "Pickup OTP is required")
                return redirect('rider:dashboard')
            
            try:
                order = Order.objects.get(id=assignment.order_id)
                if OTPService.verify_otp(order, 'PICKUP', otp_input, rider):
                    assignment.status = 'PICKED_UP'
                    assignment.save()
                    
                    from django.utils import timezone
                    # Update Order Status to PICKED_UP
                    order.status = 'PICKED_UP' 
                    order.picked_up_at = timezone.now()
                    order.save()
                    
                    messages.success(request, "Order Picked Up Verified!")
            except ValidationError as e:
                messages.error(request, str(e))
                return redirect('rider:dashboard')
            except Order.DoesNotExist:
                 messages.error(request, "Order not found")

        elif action == 'ON_THE_WAY':
            assignment.status = 'ON_THE_WAY'
            assignment.save()
            
            # Generate Delivery OTP
            try:
                order = Order.objects.get(id=assignment.order_id)
                order.status = 'ON_THE_WAY' # Sync status
                order.preparing_at = order.preparing_at or timezone.now() # Fallback
                order.save()
                OTPService.generate_otp(order, 'DELIVERY')
            except Order.DoesNotExist:
                pass
                
            messages.success(request, "On the way to customer! Delivery OTP Generated.")

        elif action == 'DELIVERED':
            otp_input = request.POST.get('otp')
            if not otp_input:
                messages.error(request, "Delivery OTP is required")
                return redirect('rider:dashboard')

            try:
                order = Order.objects.get(id=assignment.order_id)
                if OTPService.verify_otp(order, 'DELIVERY', otp_input, rider):
                    assignment.status = 'DELIVERED'
                    assignment.save()
                    
                    # Update specific order fields
                    order.status = 'DELIVERED'
                    order.delivered_at = timezone.now()
                    order.payment_status = 'PAID' # Assume paid implies COD collected or Pre-paid
                    order.save()

                    # Add to wallet (Sample amount ₹40)
                    rider.wallet_balance += 40
                    rider.save()
                    # Record Earning record
                    Earning.objects.create(
                        rider=rider,
                        order_id=assignment.order_id,
                        amount=40,
                        transaction_type='DELIVERY'
                    )
                    messages.success(request, "Delivered Verified! Earning added to wallet.")
            except ValidationError as e:
                messages.error(request, str(e))
                return redirect('rider:dashboard')
            except Order.DoesNotExist:
                 messages.error(request, "Order not found")

class ToggleDutyView(View):
    @method_decorator(rider_required)
    def post(self, request):
        phone = request.session['rider_phone']
        rider = Rider.objects.get(phone=phone)
        rider.is_online = not rider.is_online
        rider.save()
        status = "Online" if rider.is_online else "Offline"
        messages.success(request, f"You are now {status}")
        return redirect('rider:dashboard')



class EarningsView(View):
    template_name = 'rider/dashboard/earnings.html'

    @method_decorator(rider_required)
    def get(self, request):
        phone = request.session['rider_phone']
        rider = Rider.objects.get(phone=phone)
        
        # Aggregations
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        daily_earnings = Earning.objects.filter(
            rider=rider, 
            timestamp__date=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        weekly_earnings = Earning.objects.filter(
            rider=rider, 
            timestamp__date__gte=week_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        all_earnings = Earning.objects.filter(rider=rider)
        payouts = Payout.objects.filter(rider=rider)

        return render(request, self.template_name, {
            'rider': rider,
            'daily_earnings': daily_earnings,
            'weekly_earnings': weekly_earnings,
            'earnings': all_earnings,
            'payouts': payouts
        })

class RequestPayoutView(View):
    @method_decorator(rider_required)
    def post(self, request):
        phone = request.session['rider_phone']
        rider = Rider.objects.get(phone=phone)
        
        if rider.wallet_balance <= 0:
            messages.error(request, "No balance to request payout.")
            return redirect('rider:earnings')
            
        amount = rider.wallet_balance
        Payout.objects.create(
            rider=rider,
            amount=amount,
            status='PENDING'
        )
        
        # Deduct from wallet immediately to prevent double requests
        rider.wallet_balance = 0
        rider.save()
        
        messages.success(request, f"Payout request for ₹{amount} submitted!")
        return redirect('rider:earnings')

class AcceptOrderView(View):
    @method_decorator(rider_required)
    def post(self, request, order_id):
        phone = request.session['rider_phone']
        rider = Rider.objects.get(phone=phone)
        
        # 1. Block if rider already has an active order
        active_assignment = OrderAssignment.objects.filter(
            rider=rider, 
            status__in=['ACCEPTED', 'PICKED_UP', 'ON_THE_WAY']
        ).exists()
        
        if active_assignment:
            messages.error(request, "You already have an active mission!")
            return redirect('rider:dashboard')
            
        from django.db import transaction
        from core.models import User as CoreUser
        
        try:
            with transaction.atomic():
                # 2. Lock the order for atomic update
                order = Order.objects.select_for_update().get(
                    id=order_id, 
                    status__in=['CONFIRMED', 'PREPARING', 'READY'], 
                    rider__isnull=True
                )
                
                # 3. Double-check if another assignment exists (Safety layer)
                if OrderAssignment.objects.filter(order_id=order_id, status__in=['ACCEPTED', 'PICKED_UP']).exists():
                     raise Order.DoesNotExist() # Treat as "no longer available"

                # 4. Perform Assignment
                rider_user = CoreUser.objects.get(phone=rider.phone, role='RIDER')
                
                from django.utils import timezone
                order.rider = rider_user
                order.status = 'ASSIGNED'
                order.assigned_at = timezone.now()
                order.save()
                
                OrderAssignment.objects.create(
                    rider=rider,
                    order_id=order.id,
                    status='ACCEPTED'
                )
                
                messages.success(request, f"Mission Accepted! Order #{order.order_id}")
                
        except Order.DoesNotExist:
            messages.error(request, "Mission no longer available or already taken.")
        except CoreUser.DoesNotExist:
            messages.error(request, "System error: Rider profile synchronization failed.")
        except Exception as e:
            messages.error(request, f"Error accepting mission: {str(e)}")
            
        return redirect('rider:dashboard')

# ... (OrderActionView update below)
