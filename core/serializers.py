from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from .models import User, Address, OTP
from django.utils import timezone
from datetime import timedelta


class SmartImageField(serializers.ImageField):
    """
    Custom ImageField that returns relative /media/ paths for local files,
    or full URLs for external/Cloudinary images.
    """
    def to_representation(self, value):
        if not value:
            return None
        image_str = str(value)
        # If already a full URL, return as-is
        if image_str.startswith('http'):
            return image_str
        # Return relative path with /media/ prefix for local files
        if image_str and not image_str.startswith('/media/'):
            return f'/media/{image_str}'
        return image_str


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False)
    
    def get_name(self, obj):
        try:
            return getattr(obj, 'name', '') or getattr(obj, 'email', '') or ''
        except Exception:
            return ''

    def get_profile_image(self, obj):
        try:
            if hasattr(obj, 'avatar') and obj.avatar:
                return obj.avatar.url if hasattr(obj.avatar, 'url') else str(obj.avatar)
            return None
        except Exception:
            return None
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'password', 'profile_image', 'role', 'is_verified', 'email_verified', 'created_at']
        read_only_fields = ['id', 'created_at']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'label', 'address_line1', 'address_line2', 'landmark', 'city', 'state', 
                  'pincode', 'latitude', 'longitude', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate(self, data):
        # Round coordinates to 6 decimal places to match database schema
        if 'latitude' in data:
            data['latitude'] = round(data['latitude'], 6)
        if 'longitude' in data:
            data['longitude'] = round(data['longitude'], 6)

        if data.get('is_default'):
            # Unset other default addresses
            if self.instance:
                Address.objects.filter(user=self.instance.user, is_default=True).exclude(id=self.instance.id).update(is_default=False)
            else:
                Address.objects.filter(user=self.context['request'].user, is_default=True).update(is_default=False)
        return data


class OTPSendSerializer(serializers.Serializer):
    """Serializer for sending OTP via email"""
    email = serializers.EmailField(required=True)
    purpose = serializers.CharField(max_length=20, required=False, default='LOGIN')
    
    def validate_email(self, value):
        """Validate email format"""
        if not value or '@' not in value:
            raise serializers.ValidationError("Invalid email address")
        return value.lower().strip()
    
    def validate_purpose(self, value):
        """Validate OTP purpose"""
        valid_purposes = ['LOGIN', 'REGISTER', 'PIN_RESET']
        if value.upper() not in valid_purposes:
            raise serializers.ValidationError(f"Purpose must be one of: {', '.join(valid_purposes)}")
        return value.upper()


class OTPVerifySerializer(serializers.Serializer):
    """Serializer for verifying OTP (email-based only)"""
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(max_length=6, required=True)
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    role = serializers.CharField(max_length=20, required=False, default='CLIENT')
    password = serializers.CharField(required=False, write_only=True)

    def validate_email(self, value):
        """Validate email format"""
        if not value or '@' not in value:
            raise serializers.ValidationError("Invalid email address")
        return value.lower().strip()
    
    def validate_otp_code(self, value):
        """Validate OTP code format"""
        value_str = str(value).strip()
        if not value_str or len(value_str) < 4:
            raise serializers.ValidationError("OTP must be at least 4 digits")
        if not value_str.isdigit():
            raise serializers.ValidationError("OTP must contain only digits")
        return value_str

    def validate_role(self, value):
        """Validate and standardize role"""
        if value:
            return str(value).upper()
        return 'CLIENT'

    def validate_name(self, value):
        """Validate name for registration"""
        if value:
            return value.strip()
        return None


class LoginSerializer(serializers.Serializer):
    """Serializer for email + password login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    def validate_email(self, value):
        """Validate email format"""
        if not value or '@' not in value:
            raise serializers.ValidationError("Invalid email address")
        return value.lower().strip()


class RegistrationSerializer(serializers.Serializer):
    """Serializer for email-based user registration"""
    email = serializers.EmailField(required=True)
    name = serializers.CharField(max_length=255, required=True)
    otp_code = serializers.CharField(max_length=6, required=True)
    role = serializers.CharField(max_length=20, required=False, default='CLIENT')
    password = serializers.CharField(required=False, write_only=True)

    def validate_email(self, value):
        """Validate email is not already registered"""
        if value and User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("Email is already registered")
        return value.lower().strip()
    
    def validate_name(self, value):
        """Validate name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required")
        return value.strip()
    
    def validate_otp_code(self, value):
        """Validate OTP code"""
        value_str = str(value).strip()
        if not value_str.isdigit() or len(value_str) < 4:
            raise serializers.ValidationError("Invalid OTP format")
        return value_str


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data
