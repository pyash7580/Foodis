from rest_framework import serializers
from client.models import Restaurant, MenuItem, MenuItemCustomization, CustomizationOption, Order, OrderItem, Coupon
from .models import RestaurantProfile, RestaurantEarnings, OrderStatusUpdate
from core.serializers import SmartImageField


class CouponSerializer(serializers.ModelSerializer):
    valid_from = serializers.DateTimeField(required=False)
    valid_until = serializers.DateTimeField(required=False)

    class Meta:
        model = Coupon
        fields = ['id', 'code', 'description', 'discount_type', 'discount_value',
                  'min_order_amount', 'max_discount', 'valid_from', 'valid_until',
                  'usage_limit', 'used_count', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at', 'used_count']


class RestaurantProfileSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    
    class Meta:
        model = RestaurantProfile
        fields = ['id', 'restaurant', 'restaurant_name', 'gst_number', 'pan_number', 'fssai_license',
                  'bank_account_number', 'ifsc_code', 'bank_name', 'created_at', 'updated_at']


class RestaurantSerializer(serializers.ModelSerializer):
    image = SmartImageField(required=False, allow_null=True)
    cover_image = SmartImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    profile = RestaurantProfileSerializer(read_only=True)
    
    def get_image_url(self, obj):
        try:
            if hasattr(obj, 'image') and obj.image:
                url = str(obj.image)
                # Return relative path with /media/ prefix
                if url and not url.startswith('http'):
                    return f'/media/{url}' if not url.startswith('/media/') else url
                return url
            return None
        except Exception:
            return None

    def get_cover_image_url(self, obj):
        try:
            if hasattr(obj, 'cover_image') and obj.cover_image:
                url = str(obj.cover_image)
                # Return relative path with /media/ prefix
                if url and not url.startswith('http'):
                    return f'/media/{url}' if not url.startswith('/media/') else url
                return url
            return None
        except Exception:
            return None
    
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'slug', 'description', 'image', 'cover_image', 'image_url', 'cover_image_url',
                  'phone', 'email', 'address', 'city', 'state', 'pincode',
                  'latitude', 'longitude', 'rating', 'total_ratings',
                  'delivery_time', 'delivery_fee', 'min_order_amount',
                  'is_veg', 'is_active', 'status', 'commission_rate', 'profile']


class MenuItemSerializer(serializers.ModelSerializer):
    image = SmartImageField(required=False, allow_null=True)
    image_url = serializers.ReadOnlyField(source='get_image_url')
    
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'image', 'image_url', 'price', 'veg_type',
                  'category', 'is_available', 'preparation_time', 'rating',
                  'total_orders', 'created_at', 'updated_at']


class CustomizationOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomizationOption
        fields = ['id', 'name', 'price', 'is_available']


class MenuItemCustomizationSerializer(serializers.ModelSerializer):
    options = CustomizationOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = MenuItemCustomization
        fields = ['id', 'name', 'is_required', 'max_selections', 'options']


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_name', 'quantity', 'price',
                  'customizations', 'subtotal']


from client.serializers import PublicRiderSerializer

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    rider = PublicRiderSerializer(read_only=True)
    rider_name = serializers.CharField(source='rider.name', read_only=True, allow_null=True)
    
    pickup_otp = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'order_id', 'user', 'user_name', 'user_phone', 'restaurant',
                  'rider', 'rider_name', 'delivery_address', 'delivery_latitude',
                  'delivery_longitude', 'delivery_phone', 'delivery_instructions', 
                  'subtotal', 'delivery_fee', 'discount', 'tax', 'total', 
                  'coupon', 'status', 'payment_method', 'payment_status', 
                  'items', 'pickup_otp', 'delivery_otp',
                  'placed_at', 'confirmed_at', 'preparing_at', 'ready_at',
                  'picked_up_at', 'delivered_at', 'rider_latitude',
                  'rider_longitude', 'estimated_delivery_time']

    def get_pickup_otp(self, obj):
        if obj.pickup_otp:
            return obj.pickup_otp
        
        # Fallback to Cache via OTPService
        from client.services.otp_service import OTPService
        return OTPService.get_valid_otp(obj, 'PICKUP')


class RestaurantEarningsSerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(source='order.order_id', read_only=True)
    
    class Meta:
        model = RestaurantEarnings
        fields = ['id', 'restaurant', 'order', 'order_id', 'order_total',
                  'commission', 'net_amount', 'date', 'created_at']


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source='updated_by.name', read_only=True, allow_null=True)
    
    class Meta:
        model = OrderStatusUpdate
        fields = ['id', 'order', 'status', 'updated_by', 'updated_by_name',
                  'notes', 'created_at']

