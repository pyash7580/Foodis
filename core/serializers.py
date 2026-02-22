from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from .models import User, Address, OTP
from django.utils import timezone
from datetime import timedelta


class SmartImageField(serializers.ImageField):
    """
    Custom ImageField that returns the raw string if it starts with http,
    otherwise uses the standard DRF ImageField behavior.
    """
    def to_representation(self, value):
        if not value:
            return None
        image_str = str(value)
        if image_str.startswith('http'):
            return image_str
        try:
            return super().to_representation(value)
        except Exception as getattr_fail:
            return None


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False)
    
    def get_name(self, obj):
        try:
            return getattr(obj, 'name', '') or getattr(obj, 'phone', '') or getattr(obj, 'email', '') or ''
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
        fields = ['id', 'phone', 'email', 'name', 'password', 'profile_image', 'role', 'created_at']
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
    phone = serializers.CharField(max_length=17, required=False)
    mobile = serializers.CharField(max_length=17, required=False)
    email = serializers.EmailField(required=False)
    
    def validate_phone(self, value):
        # Standardize phone to 10 digits
        if value:
            digits = ''.join(filter(str.isdigit, str(value)))
            if len(digits) >= 10:
                return digits[-10:]
            raise serializers.ValidationError("Phone number must be at least 10 digits.")
        return value

    def validate_mobile(self, value):
        return self.validate_phone(value)

    def validate(self, data):
        # Allow 'mobile' as an alias for 'phone'
        if 'mobile' in data and not data.get('phone'):
            data['phone'] = data.pop('mobile')
            
        if not data.get('phone') and not data.get('email'):
            raise serializers.ValidationError("Either phone or email is required")
        return data


class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=17, required=False)
    mobile = serializers.CharField(max_length=17, required=False)
    email = serializers.EmailField(required=False)
    otp_code = serializers.CharField(max_length=6, required=True)
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    role = serializers.CharField(max_length=20, required=False, allow_blank=True)
    password = serializers.CharField(required=False, write_only=True)

    def validate_phone(self, value):
        # Standardize phone to 10 digits
        if value:
            val_str = str(value)
            digits = ''.join(filter(str.isdigit, val_str))
            
            # If user enters +911234567890 (length 12), take last 10
            # If user enters 1234567890 (length 10), take as is
            if len(digits) >= 10:
                return digits[-10:]
            
            raise serializers.ValidationError("Phone number must be at least 10 digits.")
        return value

    def validate_mobile(self, value):
        return self.validate_phone(value)

    def validate_role(self, value):
        if value:
            # Standardize role to uppercase to match User.ROLE_CHOICES
            return str(value).upper()
        return value

    def validate(self, data):
        # Allow 'mobile' as an alias for 'phone'
        if 'mobile' in data and not data.get('phone'):
            data['phone'] = data.pop('mobile')

        if not data.get('phone') and not data.get('email'):
            raise serializers.ValidationError("Either phone or email is required")
        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()  # Changed from EmailField to accept phone numbers too
    password = serializers.CharField(write_only=True)


class RegistrationSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=17, required=True)
    name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    role = serializers.CharField(max_length=20, default='CLIENT')

    def validate_phone(self, value):
        if value:
            digits = ''.join(filter(str.isdigit, str(value)))
            if len(digits) >= 10:
                return digits[-10:]
            raise serializers.ValidationError("Phone number must be at least 10 digits.")
        return value



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
