from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Rider

User = get_user_model()

class RiderRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    name = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = ('phone', 'name', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            phone=validated_data['phone'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            name=validated_data['name'],
            role='RIDER'
        )
        
        # Automatically create Rider profile
        Rider.objects.create(
            phone=user.phone,
            full_name=user.name,
            is_active=True,
            is_online=False
        )
        
        return user

class RiderProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rider
        fields = ('phone', 'full_name', 'city', 'is_active', 'is_online', 'wallet_balance', 'total_distance')
        read_only_fields = ('phone', 'wallet_balance', 'total_distance')

class RiderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rider
        fields = ('status',)
