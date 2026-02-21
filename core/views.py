from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
# [MODIFIED]: Elevated commonly used imports
from django.contrib.auth import get_user_model, authenticate, logout
from .serializers import (
    UserSerializer, AddressSerializer, OTPSendSerializer, 
    OTPVerifySerializer, LoginSerializer, RegistrationSerializer
)
from .utils import send_otp, verify_otp, send_email_otp, verify_email_otp
from .models import Address
from django.conf import settings
from django.utils import timezone
import os
import traceback
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


def normalize_phone(phone):
    """Normalize phone to last 10 digits for consistent auth lookups."""
    if not phone:
        return ""
    digits = ''.join(filter(str.isdigit, str(phone)))
    return digits[-10:] if len(digits) >= 10 else digits


def find_user_by_phone(phone):
    """Find user using multiple phone formats (+91, 91, plain 10-digit)."""
    normalized = normalize_phone(phone)
    if not normalized:
        return None

    candidates = [normalized, f"+91{normalized}", f"91{normalized}"]
    user = User.objects.filter(phone__in=candidates).first()
    if user:
        return user

    return User.objects.filter(phone__endswith=normalized).first()

def log_debug(message):
    """Consolidated debug logging to file"""
    try:
        log_path = os.path.join(settings.BASE_DIR, 'otp_debug.log')
        with open(log_path, 'a') as f:
            f.write(f"[{timezone.now()}] {message}\n")
    except Exception:
        pass


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def auth_root_view(request):
    """Auth API root endpoint showing available authentication endpoints"""
    return Response({
        "name": "Foodis Auth API",
        "description": "Endpoints for user authentication, profile management, and configuration",
        "endpoints": {
            "send_otp": "/api/auth/send-otp/",
            "verify_otp": "/api/auth/verify-otp/",
            "login": "/api/auth/login/",
            "logout": "/api/auth/logout/",
            "profile": "/api/auth/profile/",
            "update_profile": "/api/auth/profile/update/",
            "config": "/api/auth/config/",
            "addresses": "/api/auth/addresses/"
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def home_view(request):
    """Root API endpoint showing status and available routes"""
    return Response({
        "name": "Foodis API",
        "status": "online",
        "message": "Welcome to the Foodis Backend API",
        "version": "1.0.0",
        "endpoints": {
            "admin": "/admin/",
            "auth": "/api/auth/",
            "client": "/api/client/",
            "restaurant": "/api/restaurant/",
            "rider": "/api/rider/",
            "admin_api": "/api/admin/",
            "ai": "/api/ai/"
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_otp_view(request):
    """API for sending OTP to phone or email"""
    import logging
    
    # 📝 FORCE LOG EVERYTHING
    # [MODIFIED]: Cleaned up try/open logic with the helper method
    log_debug(f"\n--- [{timezone.now()}] SEND OTP REQUEST ---\nDATA: {request.data}")

    try:
        serializer = OTPSendSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data.get('phone')
            email = serializer.validated_data.get('email')
            
            otp_code = None
            flow = "REGISTER"
            is_registered = False

            if phone:
                clean_phone_num = normalize_phone(phone)
                user = find_user_by_phone(clean_phone_num)
                is_registered = user is not None
                if user:
                    flow = "LOGIN"
                    
                logger.debug(f"Calling send_otp for phone: {phone}")
                otp_code = send_otp(phone)
            elif email:
                user = User.objects.filter(email=email).first()
                is_registered = user is not None
                if user:
                    flow = "LOGIN"
                    
                logger.debug(f"Calling send_email_otp for email: {email}")
                otp_code = send_email_otp(email)
            
            return Response({
                'message': 'OTP sent successfully',
                'otp': otp_code,  # Remove in production
                'flow': flow,
                'is_registered': is_registered,
                'is_new_user': not is_registered
            }, status=status.HTTP_200_OK)
        
        # Validation Failed
        errors = serializer.errors
        log_debug(f"VALIDATION FAILED: {errors}")
        return Response({
            "error": "INVALID_DATA", 
            "message": "Validation failed", 
            "details": errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        # 🚨 CRASH CAPTURE
        tb = traceback.format_exc()
        log_debug(f"CRASH IN send_otp_view: {str(e)}\n{tb}")
        
        response_data = {
            "error": "SERVER_ERROR", 
            "message": "Failed to send OTP", 
            "details": str(e)
        }
        if settings.DEBUG:
            response_data["traceback"] = tb
            
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_otp_view(request):
    """API for verifying OTP and logging in/initiating registration"""
    import traceback
    
    # 📝 FORCE LOG EVERYTHING
    log_debug(f"\n--- [{timezone.now()}] VERIFY OTP REQUEST ---\nDATA: {request.data}")

    try:
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data.get('phone')
            email = serializer.validated_data.get('email')
            otp_code = serializer.validated_data['otp_code']
            role_requested = serializer.validated_data.get('role', 'CLIENT')

            is_verified = False
            if phone:
                is_verified = verify_otp(phone, otp_code)
            elif email:
                is_verified = verify_email_otp(email, otp_code)

            if is_verified:
                # Check if user exists
                user = None
                if phone:
                    clean_phone_num = normalize_phone(phone)
                    # 🔍 DEBUG: Check exact string and query
                    log_debug(f"LOOKUP: clean_phone_num='{clean_phone_num}'")
                    
                    user = find_user_by_phone(clean_phone_num)
                    
                    log_debug(f"FOUND USER: {user} (ID: {user.id if user else 'None'})")
                elif email:
                    user = User.objects.filter(email=email).first()

                if user:
                    created = False
                else:
                    # 📌 USER DOES NOT EXIST -> REGISTER directly here
                    log_debug(f"REGISTER: Phone/Email {phone or email} not found in DB. Creating new user.")
                    if phone:
                        clean_phone_num = normalize_phone(phone)
                        user = User.objects.create(
                            phone=clean_phone_num,
                            role='CLIENT',
                            is_verified=True,
                            is_active=True
                        )
                    elif email:
                        user = User.objects.create(
                            email=email,
                            role='CLIENT',
                            is_verified=True,
                            is_active=True
                        )
                    created = True

                # SECURE ROLE CHECK
                # If user exists but role mismatch, return error to prevent wrong portal login
                if not created and role_requested and user.role != role_requested:
                    log_debug(f"ROLE MISMATCH: User {user.phone} is {user.role}, but requested {role_requested}")
                    
                    return Response({
                        "error": "ROLE_MISMATCH",
                        "message": f"This number is registered as a {user.role.capitalize()}. Please use the correct login page.",
                        "registered_role": user.role
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # 📌 USER LOGIN / CREATED
                refresh = RefreshToken.for_user(user)
                refresh['role'] = user.role
                
                response_data = {
                    "action": "LOGIN",
                    "message": "OTP verified successfully",
                    "token": str(refresh.access_token),
                    "refresh": str(refresh),
                    "is_new_user": created,
                    "user": UserSerializer(user, context={'request': request}).data
                }

                # Role redirection logic
                if user.role == 'RIDER':
                    # ... rider logic ...
                    try:
                        from rider_legacy.models import RiderProfile
                        profile = RiderProfile.objects.filter(rider=user).first()
                        if profile:
                            if profile.status == 'APPROVED' and profile.is_onboarding_complete:
                                response_data['redirect_to'] = 'dashboard'
                            elif profile.status == 'UNDER_REVIEW':
                                response_data['redirect_to'] = 'status'
                            elif profile.status == 'REJECTED':
                                response_data['redirect_to'] = 'rejected'
                            elif profile.status == 'BLOCKED':
                                response_data['redirect_to'] = 'blocked'
                            else:
                                response_data['redirect_to'] = 'onboarding'
                                response_data['step'] = profile.onboarding_step
                            response_data['rider_status'] = profile.status
                        else:
                            response_data['redirect_to'] = 'onboarding'
                            response_data['step'] = 0
                            response_data['rider_status'] = 'NEW'
                    except Exception as e:
                        log_debug(f"Error fetching rider profile: {e}")
                
                log_debug(f"SUCCESS: User {user.phone} logged in as {user.role}")
                
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                log_debug(f"FAILURE: Invalid or Expired OTP for {phone or email}")
                return Response({
                    "error": "INVALID_OTP", 
                    "message": "Invalid or expired OTP", 
                    "details": "The OTP code provided is incorrect, already used, or has expired."
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validation Failed
        log_debug(f"VERIFY VALIDATION FAILED: {serializer.errors}")
        return Response({"error": "INVALID_DATA", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        # 🚨 CRASH CAPTURE
        log_debug(f"CRASH IN verify_otp_view: {str(e)}\n{traceback.format_exc()}")
        return Response({"error": "SERVER_ERROR", "message": "Verification crashed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    """Create a new user after OTP verification"""
    from .serializers import RegistrationSerializer
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        phone = serializer.validated_data.get('phone')
        email = serializer.validated_data.get('email')
        name = serializer.validated_data.get('name')
        role = serializer.validated_data.get('role', 'CLIENT')
        normalized_phone = normalize_phone(phone)

        # Double check if user already exists (including legacy +91 formats)
        if find_user_by_phone(normalized_phone):
             return Response({"error": "User with this phone number already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        if email and User.objects.filter(email=email).exists():
             return Response({"error": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Create user
        user = User.objects.create(
            phone=normalized_phone,
            email=email if email else None,
            name=name,
            role=role,
            is_verified=True,
            is_active=True
        )
        
        refresh = RefreshToken.for_user(user)
        refresh['role'] = user.role
        
        return Response({
            "message": "User registered successfully",
            "token": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user, context={'request': request}).data,
            "action": "LOGIN"
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Login with email and password"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email'].strip()
        password = serializer.validated_data['password']
        
        # Authenticate user
        user = None
        try:
             # Authenticate user
             user = authenticate(username=email, password=password)
             print(f"DEBUG: authenticate() result: {user}")
             
             if not user:
                 User = get_user_model()
                 try:
                     # Try finding by Email
                     user_obj = User.objects.filter(email__iexact=email).first()
                     
                     if not user_obj and email.lower() == 'admin':
                          user_obj = User.objects.filter(role='ADMIN', is_superuser=True).first()

                     # Try finding by Phone using normalized and legacy formats
                     if not user_obj:
                         user_obj = find_user_by_phone(email)

                     if user_obj:
                         print(f"DEBUG: Found user by lookup: {getattr(user_obj, 'email', '') or getattr(user_obj, 'phone', '')}")
                         if user_obj.check_password(password):
                             user = user_obj
                             print("DEBUG: Password check passed")
                         else:
                             print("DEBUG: Password check failed")
                     else:
                          print("DEBUG: User not found by email or phone")
                 except Exception as e:
                     print(f"DEBUG: Lookup error: {e}")
                     pass
        except Exception as e:
             print(f"DEBUG: Exception during auth: {e}")
             pass

        if user:
            if not user.is_active:
                return Response({'error': 'User account is disabled.'}, status=status.HTTP_400_BAD_REQUEST)

            refresh = RefreshToken.for_user(user)
            refresh['role'] = user.role
            return Response({
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
            
    print(f"DEBUG: Serializer errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout user by blacklisting tokens if using blacklisting, or just destroying session"""
    # SimpleJWT tokens are stateless, so we don't necessarily "delete" them 
    # unless we use the token blacklist app.
    # For now, we'll just destroy the session for cookie-based auth.
    
    logout(request)
    
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    """Get user profile with stats"""
    user = request.user
    serializer = UserSerializer(user, context={'request': request})
    data = serializer.data
    
    # Calculate stats
    try:
        from client.models import Order
        from django.db.models import Sum
        
        # Only count valid orders (not cancelled/failed payment) for spend
        # For total orders, we might want all or just completed. Zomato usually shows all placed.
        data['total_orders'] = Order.objects.filter(user=user).count()
        
        total_spent = Order.objects.filter(
            user=user, 
            payment_status='PAID'
        ).aggregate(total=Sum('total'))['total']
        
        data['total_spent'] = float(total_spent) if total_spent else 0.0
        
    except ImportError:
        # Fallback if client app not ready or circular import
        data['total_orders'] = 0
        data['total_spent'] = 0.0
        
    return Response(data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_profile_view(request):
    """Update user profile"""
    print(f"DEBUG: Update Profile Request Data: {request.data}")
    serializer = UserSerializer(request.user, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    print(f"DEBUG: Update Profile Errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressListCreateView(generics.ListCreateAPIView):
    """List and create addresses"""
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an address"""
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_config_view(request):
    """Get public configuration"""
    return Response({
        'razorpay_key': settings.RAZORPAY_KEY_ID
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check_view(request):
    """Simple health check endpoint"""
    return Response({
        "status": "healthy",
        "timestamp": timezone.now(),
        "backend": "django"
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def seed_riders_view(request):
    """Temporary endpoint to seed riders from file"""
    import os
    import re
    import random
    from rider_legacy.models import RiderProfile, RiderBank
    from rider.models import Rider as TemplateRider
    
    file_path = os.path.join(settings.BASE_DIR, 'RIDER_DETAILS.txt')
    if not os.path.exists(file_path):
        return Response({'error': 'File not found'}, status=404)
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        count = 0
        updated = 0
        logs = []

        for line in lines:
            if line.startswith('=') or line.startswith('ID') or not line.strip() or '|' not in line:
                continue
            
            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 12: 
                continue
                
            # Mapping based on RIDER_DETAILS.txt:
            # 0:ID, 1:Name, 2:Email, 3:Pass, 4:Phone, 5:Vehicle, 6:License, 
            # 7:AccName, 8:AccNo, 9:IFSC, 10:Bank, 11:Status, 12:City

            data = {
                'name': parts[1],
                'email': parts[2],
                'password': parts[3],
                'phone': parts[4],
                'vehicle': parts[5],
                'license': parts[6],
                'acc_name': parts[7],
                'acc_no': parts[8],
                'ifsc': parts[9],
                'bank_name': parts[10],
                'status': parts[11],
                'city': parts[12] if len(parts) > 12 else ''
            }
            
            # Basic validation
            raw_phone = re.sub(r'\D', '', data['phone'])
            if len(raw_phone) > 10:
                phone = raw_phone[-10:]
            elif len(raw_phone) == 10:
                phone = raw_phone
            else:
                continue

            # 1. Create/Update User (Core Auth)
            user, created = User.objects.get_or_create(
                phone=phone,
                defaults={
                    'name': data['name'],
                    'email': data['email'] or f"rider{phone}@example.com",
                    'role': 'RIDER',
                    'is_active': True,
                    'is_verified': True
                }
            )
            
            # Always sync password if provided
            if data['password']:
                user.set_password(data['password'])
                user.save()
            elif created:
                user.set_password('password123')
                user.save()

            if created:
                count += 1
            else:
                updated += 1
                
            # 2. Create/Update Profile (rider_legacy - API/React)
            profile, _ = RiderProfile.objects.get_or_create(rider=user)
            profile.vehicle_number = data['vehicle'] if data['vehicle'] != 'N/A' else f"GJ-01-XX-{random.randint(1000,9999)}"
            profile.vehicle_type = 'BIKE'
            profile.city = data['city']
            profile.mobile_number = phone
            profile.status = 'APPROVED' # Force Approve for seeding
            profile.license_number = data['license']
            profile.is_onboarding_complete = True
            profile.save()
            
            # 3. Create/Update Bank (rider_legacy - API/React)
            bank, _ = RiderBank.objects.get_or_create(rider=user)
            bank.account_holder_name = data['acc_name']
            bank.account_number = data['acc_no']
            bank.ifsc_code = data['ifsc']
            bank.bank_name = data['bank_name']
            bank.verified = True
            bank.save()

            # 4. Create/Update Template Rider (rider - Django Templates)
            template_rider, _ = TemplateRider.objects.get_or_create(
                phone=phone,
                defaults={'full_name': data['name']}
            )
            template_rider.full_name = data['name']
            template_rider.is_active = True
            template_rider.save()
            
            logs.append(f"Processed: {user.name} ({phone})")
            
        return Response({
            'message': 'Seeding Complete',
            'created': count,
            'updated': updated,
            'logs': logs[:5]
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)

