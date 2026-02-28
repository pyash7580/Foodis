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
from .services.email_service import send_email_otp, verify_email_otp
from .models import Address
from django.conf import settings
from django.utils import timezone
import os
import traceback
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


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
    """API for sending OTP via email"""
    log_debug(f"\n--- SEND OTP REQUEST ---\nDATA: {request.data}")

    try:
        serializer = OTPSendSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            purpose = serializer.validated_data.get('purpose', 'LOGIN')

            # Check if user already exists
            user = User.objects.filter(email=email).first()
            is_registered = user is not None
            flow = "LOGIN" if is_registered else "REGISTER"

            # Send OTP email
            otp_code = send_email_otp(email, purpose=purpose)
            
            if not otp_code:
                return Response({
                    "error": "EMAIL_FAILED",
                    "message": "Failed to send OTP to your email. Please check the email address and try again.",
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'message': 'OTP sent to your email',
                'otp': otp_code if settings.DEBUG else None,  # Only for debug mode
                'flow': flow,
                'is_registered': is_registered,
                'is_new_user': not is_registered
            }, status=status.HTTP_200_OK)

        errors = serializer.errors
        log_debug(f"VALIDATION FAILED: {errors}")
        return Response({
            "error": "INVALID_DATA",
            "message": "Please provide a valid email address",
            "details": errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        tb = traceback.format_exc()
        log_debug(f"CRASH IN send_otp_view: {str(e)}\n{tb}")
        return Response({
            "error": "SERVER_ERROR",
            "message": "Failed to send OTP. Please try again.",
            "details": str(e) if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp_view(request):
    """API for verifying OTP and logging in/initiating registration"""
    log_debug(f"\n--- VERIFY OTP REQUEST ---\nDATA: {request.data}")

    try:
        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            log_debug(f"VERIFY VALIDATION FAILED: {serializer.errors}")
            return Response({
                "error": "INVALID_DATA",
                "message": "Invalid request data. Please check your input.",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get('email')
        otp_code = str(serializer.validated_data['otp_code']).strip()
        name = serializer.validated_data.get('name')
        role_requested = serializer.validated_data.get('role', 'CLIENT')

        # Verify OTP
        log_debug(f"Verifying OTP for email: {email}")
        is_verified = verify_email_otp(email, otp_code)

        if not is_verified:
            log_debug(f"FAILURE: Invalid or Expired OTP for {email}")
            return Response({
                "error": "INVALID_OTP",
                "message": "Invalid or expired OTP. Please check the code and try again.",
            }, status=status.HTTP_400_BAD_REQUEST)

        # OTP is verified — find or create user
        user = User.objects.filter(email=email).first()
        created = False

        if user:
            # Existing user login
            log_debug(f"EXISTING USER: {email}")
        else:
            # New user registration
            if not name:
                return Response({
                    "error": "MISSING_NAME",
                    "message": "Name is required for new account registration. Please provide your name.",
                }, status=status.HTTP_400_BAD_REQUEST)
            
            log_debug(f"REGISTERING NEW USER: {email}")
            user = User.objects.create(
                email=email,
                name=name.strip(),
                role=role_requested,
                is_verified=True,
                email_verified=True,
                is_active=True
            )
            created = True

        # Role mismatch check
        if not created and role_requested and user.role != role_requested:
            log_debug(f"ROLE MISMATCH: User {email} is {user.role}, but requested {role_requested}")
            return Response({
                "error": "ROLE_MISMATCH",
                "message": f"This email is registered as a {user.role.capitalize()}. Please use the correct login page.",
                "registered_role": user.role
            }, status=status.HTTP_403_FORBIDDEN)

        # Issue JWT tokens
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

        # Role-specific redirect logic
        if user.role == 'CLIENT':
            response_data['redirect_to'] = 'home'
        elif user.role == 'RESTAURANT':
            try:
                from client.models import Restaurant
                restaurant = Restaurant.objects.filter(owner=user).first()
                if restaurant:
                    response_data['redirect_to'] = 'dashboard'
                    response_data['restaurant_id'] = restaurant.id
                else:
                    response_data['redirect_to'] = 'onboarding'
            except Exception as e:
                log_debug(f"Error fetching restaurant: {e}")
                response_data['redirect_to'] = 'dashboard'
        elif user.role == 'RIDER':
            try:
                from rider.models import Rider
                rider = Rider.objects.filter(email=user.email).first()
                if rider:
                    response_data['redirect_to'] = 'dashboard'
                    response_data['rider_id'] = rider.id
                else:
                    response_data['redirect_to'] = 'onboarding'
            except Exception as e:
                log_debug(f"Error fetching rider: {e}")
                response_data['redirect_to'] = 'dashboard'

        log_debug(f"SUCCESS: User {email} logged in as {user.role}")
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
    """Register a new user with email OTP verification"""
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data.get('email')
        otp_code = serializer.validated_data.get('otp_code')
        name = serializer.validated_data.get('name')
        role = serializer.validated_data.get('role', 'CLIENT')

        # Verify OTP first
        is_verified = verify_email_otp(email, otp_code)
        if not is_verified:
            return Response({
                "error": "INVALID_OTP",
                "message": "Invalid or expired OTP. Please try again."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({
                "error": "EMAIL_EXISTS",
                "message": "This email is already registered. Please login instead."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create user
        try:
            user = User.objects.create(
                email=email,
                name=name,
                role=role,
                is_verified=True,
                email_verified=True,
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
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return Response({
                "error": "REGISTRATION_FAILED",
                "message": "Failed to register user. Please try again.",
                "details": str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        "error": "VALIDATION_ERROR",
        "message": "Invalid registration data",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login with email and password (for restaurants, riders, admin)"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email'].strip().lower()
        password = serializer.validated_data['password']

        user = None
        try:
            # Try to authenticate using Django's authenticate function
            user = authenticate(request, username=email, password=password)
            
            # If not authenticated, try manual lookup and password check
            if not user:
                user_obj = User.objects.filter(email__iexact=email).first()
                if user_obj and user_obj.check_password(password):
                    user = user_obj
        except Exception as e:
            logger.error(f"Authentication error: {e}")

        if user:
            if not user.is_active:
                return Response({
                    'error': 'ACCOUNT_DISABLED',
                    'message': 'Your account has been disabled. Please contact support.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Issue JWT tokens
            refresh = RefreshToken.for_user(user)
            refresh['role'] = user.role
            
            return Response({
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'INVALID_CREDENTIALS',
                'message': 'Invalid email or password. Please check and try again.'
            }, status=status.HTTP_401_UNAUTHORIZED)

    return Response({
        'error': 'VALIDATION_ERROR',
        'message': 'Invalid login data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


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
                'email': str(user.email or ''),
                'first_name': first_name,
                'last_name': last_name,
                'name': (
                    full_name
                    or fallback_name
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

            if not data['email']:
                continue
            email = data['email']

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'name': data['name'],
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
                email=email,
                defaults={'full_name': data['name']}
            )
            template_rider.full_name = data['name']
            template_rider.is_active = True
            template_rider.save()

            logs.append(f"Processed: {user.name} ({email})")

        return Response({
            'message': 'Seeding Complete',
            'created': count,
            'updated': updated,
            'logs': logs[:5]
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)
