from rest_framework import serializers
from client.models import Order, OrderItem
from .models import (
    RiderProfile, RiderEarnings, RiderLocation, RiderReview, 
    RiderDocument, RiderBank, RiderNotification, IncentiveScheme, 
    RiderIncentiveProgress
)

class RiderProfileSerializer(serializers.ModelSerializer):
    rider_name = serializers.CharField(source='rider.name', read_only=True)
    rider_phone = serializers.CharField(source='rider.phone', read_only=True)
    
    # We remove regex validators here to allow flexible onboarding inputs, validation happens in frontend or clean method if needed
    
    class Meta:
        model = RiderProfile
        fields = ['id', 'rider', 'rider_name', 'rider_phone', 'mobile_number', 'profile_photo', 'vehicle_type',
                  'vehicle_number', 'license_number', 'aadhar_number', 'pan_number',
                  'is_online', 'city', 'current_latitude', 'current_longitude', 'status', 
                  'onboarding_step', 'is_onboarding_complete', 'current_order',
                  'rating', 'total_deliveries', 'wallet_balance', 'created_at', 'updated_at']
        read_only_fields = ['rider', 'rider_name', 'rider_phone', 'mobile_number', 'created_at', 'updated_at', 'rating', 'total_deliveries', 'status', 'wallet_balance', 'current_order']


class RiderDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiderDocument
        fields = ['id', 'rider', 'document_type', 'file', 'verified', 'uploaded_at']
        read_only_fields = ['rider', 'verified', 'uploaded_at']


class RiderBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiderBank
        fields = ['id', 'rider', 'account_holder_name', 'account_number', 'ifsc_code', 'bank_name', 'verified']
        read_only_fields = ['rider', 'verified']


class RiderLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiderLocation
        fields = ['id', 'rider', 'latitude', 'longitude', 'timestamp']


class OrderItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='menu_item.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'name', 'quantity', 'price', 'subtotal']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    restaurant_address = serializers.CharField(source='restaurant.address', read_only=True)
    restaurant_phone = serializers.CharField(source='restaurant.phone', read_only=True)
    restaurant_latitude = serializers.DecimalField(source='restaurant.latitude', max_digits=9, decimal_places=6, read_only=True)
    restaurant_longitude = serializers.DecimalField(source='restaurant.longitude', max_digits=9, decimal_places=6, read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    
    # Aliases for frontend consistency
    customer_name = serializers.CharField(source='user.name', read_only=True)
    customer_phone = serializers.CharField(source='delivery_phone', read_only=True)
    customer_address = serializers.CharField(source='delivery_address', read_only=True)
    total_amount = serializers.DecimalField(source='total', max_digits=10, decimal_places=2, read_only=True)
    
    pickup_otp = serializers.SerializerMethodField()
    order_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'order_id', 'restaurant', 'restaurant_name', 'restaurant_address', 'restaurant_phone',
                  'restaurant_latitude', 'restaurant_longitude', 'user', 'user_name',
                  'user_phone', 'customer_name', 'customer_phone', 'customer_address',
                  'delivery_address', 'delivery_latitude', 'delivery_longitude',
                  'delivery_phone', 'delivery_instructions', 'total', 'total_amount', 'status',
                  'placed_at', 'ready_at', 'estimated_delivery_time', 'pickup_otp', 'delivery_otp', 
                  'order_name', 'items', 'payment_method']

    def get_order_name(self, obj):
        # Concatenate item names to create an "Order Name"
        items = obj.items.all()
        if not items:
            return f"Order #{obj.order_id}"
        
        item_names = [item.menu_item.name for item in items]
        if len(item_names) > 3:
            return ", ".join(item_names[:3]) + "..."
        return ", ".join(item_names)

    def get_pickup_otp(self, obj):
        if obj.pickup_otp:
            return obj.pickup_otp
        
        # Fallback to Cache via OTPService
        from client.services.otp_service import OTPService
        return OTPService.get_valid_otp(obj, 'PICKUP')


class RiderEarningsSerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(source='order.order_id', read_only=True)
    
    class Meta:
        model = RiderEarnings
        fields = ['id', 'rider', 'order', 'order_id', 'delivery_fee', 'tip',
                  'total_earning', 'date', 'created_at']


class RiderReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    rider_name = serializers.CharField(source='rider.name', read_only=True)
    
    class Meta:
        model = RiderReview
        fields = ['id', 'user', 'user_name', 'rider', 'rider_name', 'order', 'rating', 'comment', 'created_at']
        read_only_fields = ['user']

class RiderNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiderNotification
        fields = ['id', 'rider', 'title', 'message', 'notification_type', 'is_read', 'created_at']
        read_only_fields = ['rider', 'created_at']


class IncentiveSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncentiveScheme
        fields = ['id', 'title', 'description', 'scheme_type', 'target_count', 
                  'reward_amount', 'is_active', 'start_time', 'end_time', 'created_at']


class RiderIncentiveProgressSerializer(serializers.ModelSerializer):
    scheme_details = IncentiveSchemeSerializer(source='scheme', read_only=True)
    
    class Meta:
        model = RiderIncentiveProgress
        fields = ['id', 'rider', 'scheme', 'scheme_details', 'current_count', 
                  'is_completed', 'earned_at', 'date']
        read_only_fields = ['rider', 'earned_at', 'date']
