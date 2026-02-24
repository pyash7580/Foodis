from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
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
@permission_classes([AllowAny])
def auth_root_view(request):
    return Response({
        "name": "Foodis Auth API",
        "endpoints": {
            "send_otp": "/api/auth/send-otp/",
            "verify_otp": "/api/auth/verify-otp/",
            "login": "/api/auth/login/",
            "logout": "/api/auth/logout/",
            "profile": "/api/auth/profile/",
            "users": "/api/auth/users/",
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def home_view(request):
    return Response({
        "name": "Foodis API",
        "status": "online",
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp_view(request):
    """API for sending OTP to phone or email"""
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
                # ✅ FIX 1: Always normalize to +91 format BEFORE calling send_otp
                #    so the OTP cache key is always consistent with verify_otp calls
                normalized = normalize_phone(phone)
                canonical_phone = f"+91{normalized}"

                user = find_user_by_phone(normalized)
                is_registered = user is not None
                if user:
                    flow = "LOGIN"

                log_debug(f"Calling send_otp with canonical phone: {canonical_phone}")
                # ✅ FIX 2: send_otp always receives +91XXXXXXXXXX format
                otp_code = send_otp(canonical_phone)

            elif email:
                user = User.objects.filter(email=email).first()
                is_registered = user is not None
                if user:
                    flow = "LOGIN"
                otp_code = send_email_otp(email)

            return Response({
                'message': 'OTP sent successfully',
                'otp': otp_code,  # Remove in production
                'flow': flow,
                'is_registered': is_registered,
                'is_new_user': not is_registered
            }, status=status.HTTP_200_OK)

        errors = serializer.errors
        log_debug(f"VALIDATION FAILED: {errors}")
        return Response({
            "error": "INVALID_DATA",
            "message": "Validation failed",
            "details": errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        tb = traceback.format_exc()
        log_debug(f"CRASH IN send_otp_view: {str(e)}\n{tb}")
        response_data = {
            "error": "SERVER_ERROR",
            "message": "Failed to send OTP. Please try again.",
            "details": str(e)
        }
        if settings.DEBUG:
            response_data["traceback"] = tb
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp_view(request):
    """API for verifying OTP and logging in/initiating registration"""
    log_debug(f"\n--- [{timezone.now()}] VERIFY OTP REQUEST ---\nDATA: {request.data}")

    try:
        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            log_debug(f"VERIFY VALIDATION FAILED: {serializer.errors}")
            return Response({
                "error": "INVALID_DATA",
                # ✅ FIX 3: Return human-readable message so frontend shows it directly
                "message": "Invalid request data. Please check your input.",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data.get('phone')
        email = serializer.validated_data.get('email')
        otp_code = str(serializer.validated_data['otp_code'])  # ✅ FIX 4: ensure string
        role_requested = serializer.validated_data.get('role', 'CLIENT')

        is_verified = False

        if phone:
            # ✅ FIX 5: Normalize to +91 format so it matches the cache key used in send_otp
            normalized = normalize_phone(phone)
            canonical_phone = f"+91{normalized}"
            log_debug(f"Verifying OTP for canonical phone: {canonical_phone}")

            try:
                is_verified = verify_otp(canonical_phone, otp_code)
            except Exception as e:
                log_debug(f"verify_otp() raised exception: {str(e)}\n{traceback.format_exc()}")
                return Response({
                    "error": "SERVER_ERROR",
                    # ✅ FIX 6: Human-readable message, not a raw error code
                    "message": "OTP verification service failed. Please try again.",
                    "details": str(e) if settings.DEBUG else None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif email:
            try:
                is_verified = verify_email_otp(email, otp_code)
            except Exception as e:
                log_debug(f"verify_email_otp() raised exception: {str(e)}\n{traceback.format_exc()}")
                return Response({
                    "error": "SERVER_ERROR",
                    "message": "OTP verification service failed. Please try again.",
                    "details": str(e) if settings.DEBUG else None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not is_verified:
            log_debug(f"FAILURE: Invalid or Expired OTP for {phone or email}")
            return Response({
                "error": "INVALID_OTP",
                # ✅ FIX 7: This is what the user sees — make it clear
                "message": "Invalid or expired OTP. Please check the code and try again.",
            }, status=status.HTTP_400_BAD_REQUEST)

        # OTP is verified — find or create user
        user = None
        if phone:
            normalized = normalize_phone(phone)
            log_debug(f"LOOKUP: normalized='{normalized}'")
            user = find_user_by_phone(normalized)
            log_debug(f"FOUND USER: {user} (ID: {user.id if user else 'None'})")
        elif email:
            user = User.objects.filter(email=email).first()

        if user:
            created = False
        else:
            # User not found — create new account
            log_debug(f"REGISTER: Phone/Email {phone or email} not found. Creating new user.")
            if phone:
                normalized = normalize_phone(phone)
                user = User.objects.create(
                    phone=normalized,
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

        # Role mismatch check
        if not created and role_requested and user.role != role_requested:
            log_debug(f"ROLE MISMATCH: User {user.phone} is {user.role}, but requested {role_requested}")
            return Response({
                "error": "ROLE_MISMATCH",
                "message": f"This number is registered as a {user.role.capitalize()}. Please use the correct login page.",
                "registered_role": user.role
            }, status=status.HTTP_403_FORBIDDEN)

        # Issue JWT
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

        # Rider-specific redirect logic
        if user.role == 'RIDER':
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

        log_debug(f"SUCCESS: User {user.phone or user.email} logged in as {user.role}")
        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        tb = traceback.format_exc()
        log_debug(f"CRASH IN verify_otp_view: {str(e)}\n{tb}")
        return Response({
            "error": "SERVER_ERROR",
            "message": "Verification failed due to a server error. Please try again.",
            "details": str(e) if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Create a new user after OTP verification"""
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        phone = serializer.validated_data.get('phone')
        email = serializer.validated_data.get('email')
        name = serializer.validated_data.get('name')
        role = serializer.validated_data.get('role', 'CLIENT')
        normalized_phone = normalize_phone(phone)

        if find_user_by_phone(normalized_phone):
            return Response({"error": "User with this phone number already exists"}, status=status.HTTP_400_BAD_REQUEST)

        if email and User.objects.filter(email=email).exists():
            return Response({"error": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)

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
@permission_classes([AllowAny])
def login_view(request):
    """Login with email and password"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email'].strip()
        password = serializer.validated_data['password']

        user = None
        try:
            user = authenticate(username=email, password=password)
            if not user:
                user_obj = User.objects.filter(email__iexact=email).first()
                if not user_obj and email.lower() == 'admin':
                    user_obj = User.objects.filter(role='ADMIN', is_superuser=True).first()
                if not user_obj:
                    user_obj = find_user_by_phone(email)
                if user_obj and user_obj.check_password(password):
                    user = user_obj
        except Exception as e:
            print(f"DEBUG: Exception during auth: {e}")

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

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import traceback as tb_module


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            first_name = str(getattr(user, 'first_name', '') or '')
            last_name = str(getattr(user, 'last_name', '') or '')
            full_name = f"{first_name} {last_name}".strip()
            fallback_name = str(getattr(user, 'name', '') or '')
            data = {
                'id': user.pk,
                'phone': str(getattr(user, 'phone', '') or ''),
                'email': str(user.email or ''),
                'first_name': first_name,
                'last_name': last_name,
                'name': (
                    full_name
                    or fallback_name
                    or str(getattr(user, 'phone', ''))
                    or user.email or ''
                ),
                'role': str(getattr(user, 'role', '') or ''),
                'profile_image': None,
                'wallet_balance': 0.0,
            }
            try:
                img = getattr(user, 'avatar', None) or getattr(user, 'profile_image', None)
                if img:
                    data['profile_image'] = img.url if hasattr(img, 'url') else str(img)
            except Exception:
                pass
            try:
                data['wallet_balance'] = float(user.wallet.balance)
            except Exception:
                pass
            return Response(data, status=200)
        except Exception as e:
            print("PROFILE ERROR:\n", tb_module.format_exc())
            return Response({'error': str(e)}, status=500)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_config_view(request):
    return Response({'razorpay_key': settings.RAZORPAY_KEY_ID}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_view(request):
    return Response({
        "status": "healthy",
        "timestamp": timezone.now(),
        "backend": "django"
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def seed_riders_view(request):
    """Temporary endpoint to seed riders from file"""
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

            data = {
                'name': parts[1], 'email': parts[2], 'password': parts[3],
                'phone': parts[4], 'vehicle': parts[5], 'license': parts[6],
                'acc_name': parts[7], 'acc_no': parts[8], 'ifsc': parts[9],
                'bank_name': parts[10], 'status': parts[11],
                'city': parts[12] if len(parts) > 12 else ''
            }

            raw_phone = re.sub(r'\D', '', data['phone'])
            if len(raw_phone) > 10:
                phone = raw_phone[-10:]
            elif len(raw_phone) == 10:
                phone = raw_phone
            else:
                continue

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

            profile, _ = RiderProfile.objects.get_or_create(rider=user)
            profile.vehicle_number = data['vehicle'] if data['vehicle'] != 'N/A' else f"GJ-01-XX-{random.randint(1000,9999)}"
            profile.vehicle_type = 'BIKE'
            profile.city = data['city']
            profile.mobile_number = phone
            profile.status = 'APPROVED'
            profile.license_number = data['license']
            profile.is_onboarding_complete = True
            profile.save()

            bank, _ = RiderBank.objects.get_or_create(rider=user)
            bank.account_holder_name = data['acc_name']
            bank.account_number = data['acc_no']
            bank.ifsc_code = data['ifsc']
            bank.bank_name = data['bank_name']
            bank.verified = True
            bank.save()

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
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)
