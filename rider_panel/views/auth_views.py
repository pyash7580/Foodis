from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, logout, get_user_model
from django.contrib import messages
from core.models import OTP
from django.utils import timezone
import random

User = get_user_model()

class LoginView(View):
    template_name = 'rider_panel/auth/login.html'

    def get(self, request):
        if request.user.is_authenticated and request.user.role == 'RIDER':
            return redirect('rider_panel:dashboard')
        return render(request, self.template_name)

    def post(self, request):
        phone = request.POST.get('phone')
        if not phone:
            messages.error(request, "Phone number is required")
            return render(request, self.template_name)

        # Check if user exists and is a rider
        try:
            user = User.objects.get(phone=phone, role='RIDER')
        except User.DoesNotExist:
            messages.error(request, "No rider account found for this number")
            return render(request, self.template_name)

        # Generate and save OTP
        otp_code = str(random.randint(100000, 999999))
        expiry = timezone.now() + timezone.timedelta(minutes=5)
        
        OTP.objects.filter(phone=phone).delete()  # Clear old ones
        OTP.objects.create(
            phone=phone,
            otp_code=otp_code,
            expires_at=expiry
        )

        # For development, we store it in session to show on next page (simulation)
        request.session['auth_phone'] = phone
        messages.success(request, f"OTP sent to {phone} (Simulation: {otp_code})")
        return redirect('rider_panel:verify_otp')

class VerifyOTPView(View):
    template_name = 'rider_panel/auth/otp_verify.html'

    def get(self, request):
        phone = request.session.get('auth_phone')
        if not phone:
            return redirect('rider_panel:login')
        return render(request, self.template_name, {'phone': phone})

    def post(self, request):
        phone = request.session.get('auth_phone')
        otp_input = request.POST.get('otp')

        if not phone:
            return redirect('rider_panel:login')

        try:
            otp_obj = OTP.objects.get(phone=phone, otp_code=otp_input, is_verified=False)
            if otp_obj.is_expired():
                messages.error(request, "OTP expired")
                return render(request, self.template_name, {'phone': phone})
            
            # Success
            user = User.objects.get(phone=phone, role='RIDER')
            login(request, user)
            
            otp_obj.is_verified = True
            otp_obj.save()
            
            del request.session['auth_phone']
            return redirect('rider_panel:dashboard')

        except OTP.DoesNotExist:
            messages.error(request, "Invalid OTP")
            return render(request, self.template_name, {'phone': phone})

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('rider_panel:login')
