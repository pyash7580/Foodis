from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Rider

User = get_user_model()

class RiderRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('email', 'name', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            role='RIDER'
        )
        
        # Automatically create Rider profile
        Rider.objects.create(
            email=user.email,
            full_name=user.name,
            is_active=True,
            status='OFFLINE'
        )
        
        return user

class RiderProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rider
        fields = ('email', 'full_name', 'city', 'is_active', 'status', 'wallet_balance')
        read_only_fields = ('email', 'wallet_balance')

class RiderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rider
        fields = ('status',)
