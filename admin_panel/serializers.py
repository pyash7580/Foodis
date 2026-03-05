from rest_framework import serializers
from django.contrib.auth import get_user_model
from client.models import Restaurant, Order, OrderItem, Coupon, Wallet, WalletTransaction, Review, MenuItem, Category

from restaurant.models import RestaurantEarnings
from rider_legacy.models import RiderProfile, RiderEarnings, RiderBank
from rider.models import Rider
from .models import Banner, Commission, SitePolicy, SystemSettings

User = get_user_model()



class UserSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField()
    total_orders = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'is_active', 
                  'is_verified', 'created_at', 'last_login', 
                  'city', 'total_orders', 'total_spent']
    
    def get_city(self, obj):
        address = obj.addresses.filter(is_default=True).first() or obj.addresses.first()
        return address.city if address else 'N/A'

    def get_total_orders(self, obj):
        # Avoid circular import issues by importing locally if needed, 
        # though models are already imported at top of file usually.
        # Check imports: from client.models import Order is there.
        # But 'obj' is a User instance. Relation is reverse foreign key?
        # Order model has 'user' FK. So obj.order_set.count() works if related_name is default or specific.
        # Order model in client/models.py: user = models.ForeignKey(User, ...)
        return Order.objects.filter(user=obj).count()

    def get_total_spent(self, obj):
        from django.db.models import Sum
        total = Order.objects.filter(user=obj, payment_status='PAID').aggregate(Sum('total'))['total__sum']
        return total if total else 0.0



class RestaurantSerializer(serializers.ModelSerializer):
    # Read-only fields for displaying owner info
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    owner_phone = serializers.CharField(source='owner.phone', read_only=True)
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    owner_password = serializers.CharField(source='owner.password', read_only=True)
    
    # Write-only fields for creating owner account
    create_owner_name = serializers.CharField(write_only=True, required=False)
    create_owner_phone = serializers.CharField(write_only=True, required=False)
    create_owner_email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    
    # Field to return generated password after creation
    generated_password = serializers.CharField(read_only=True)
    
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'slug', 'owner', 'owner_name', 'owner_phone', 'owner_email', 'owner_password',
                  'email', 'address', 'city', 'state', 'pincode',
                  'status', 'rating', 'total_ratings', 'is_active',
                  'image', 'cover_image', 'cuisine', 'description', 'latitude', 'longitude',
                  'delivery_time', 'delivery_fee', 'min_order_amount', 'commission_rate', 'is_veg',
                  'create_owner_name', 'create_owner_phone', 'create_owner_email', 'generated_password',
                  'created_at', 'updated_at']
        read_only_fields = ['generated_password']


class RiderBankSerializer(serializers.ModelSerializer):
    """Serializer for RiderBank details"""
    class Meta:
        model = RiderBank
        fields = ['account_holder_name', 'account_number', 'ifsc_code', 'bank_name', 'verified']


class RiderSerializer(serializers.ModelSerializer):
    """Serializer for rider.Rider — the active rider model with extended profile info"""
    
    rider_name = serializers.SerializerMethodField()
    rider_phone = serializers.SerializerMethodField()
    rider_email = serializers.SerializerMethodField()
    vehicle_number = serializers.SerializerMethodField()
    vehicle_type = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    profile_status = serializers.SerializerMethodField()
    license_number = serializers.SerializerMethodField()
    aadhar_number = serializers.SerializerMethodField()
    pan_number = serializers.SerializerMethodField()
    total_deliveries = serializers.SerializerMethodField()
    bank_details = serializers.SerializerMethodField()

    class Meta:
        model = Rider
        fields = ['id', 'email', 'full_name', 'city', 'status', 'is_online', 'is_active',
                  'wallet_balance', 'current_latitude', 'current_longitude',
                  'rider_name', 'rider_phone', 'rider_email', 'vehicle_number', 'vehicle_type', 
                  'rating', 'profile_status', 'license_number', 'aadhar_number', 'pan_number',
                  'total_deliveries', 'bank_details', 'created_at', 'updated_at']

    def get_rider_name(self, obj):
        """Get name from Rider object"""
        return obj.full_name

    def get_rider_phone(self, obj):
        """Get phone from RiderProfile if it exists"""
        try:
            from core.models import User
            user = User.objects.filter(email=obj.email).first()
            if user and hasattr(user, 'rider_profile'):
                return user.rider_profile.mobile_number or 'N/A'
        except:
            pass
        return 'N/A'

    def get_rider_email(self, obj):
        """Get email from Rider object"""
        return obj.email

    def get_vehicle_number(self, obj):
        """Get vehicle number from RiderProfile if it exists"""
        try:
            from core.models import User
            user = User.objects.filter(email=obj.email).first()
            if user and hasattr(user, 'rider_profile'):
                return user.rider_profile.vehicle_number or 'N/A'
        except:
            pass
        return 'N/A'

    def get_vehicle_type(self, obj):
        """Get vehicle type from RiderProfile if it exists"""
        try:
            from core.models import User
            user = User.objects.filter(email=obj.email).first()
            if user and hasattr(user, 'rider_profile'):
                return user.rider_profile.vehicle_type or 'N/A'
        except:
            pass
        return 'N/A'

    def get_rating(self, obj):
        """Get rating from RiderProfile if it exists"""
        try:
            from core.models import User
            user = User.objects.filter(email=obj.email).first()
            if user and hasattr(user, 'rider_profile'):
                rating = user.rider_profile.rating
                return float(rating) if rating else 0.0
        except:
            pass
        return 0.0

    def get_profile_status(self, obj):
        """Get profile status from RiderProfile if it exists"""
        try:
            from core.models import User
            user = User.objects.filter(email=obj.email).first()
            if user and hasattr(user, 'rider_profile'):
                return user.rider_profile.status or 'NEW'
        except:
            pass
        return 'NEW'

    def get_license_number(self, obj):
        """Get license number from RiderProfile if it exists"""
        try:
            from core.models import User
            user = User.objects.filter(email=obj.email).first()
            if user and hasattr(user, 'rider_profile'):
                return user.rider_profile.license_number or None
        except:
            pass
        return None

    def get_aadhar_number(self, obj):
        """Get aadhar number from RiderProfile if it exists"""
        try:
            from core.models import User
            user = User.objects.filter(email=obj.email).first()
            if user and hasattr(user, 'rider_profile'):
                return user.rider_profile.aadhar_number or None
        except:
            pass
        return None

    def get_pan_number(self, obj):
        """Get PAN number from RiderProfile if it exists"""
        try:
            from core.models import User
            user = User.objects.filter(email=obj.email).first()
            if user and hasattr(user, 'rider_profile'):
                return user.rider_profile.pan_number or None
        except:
            pass
        return None

    def get_total_deliveries(self, obj):
        """Get total deliveries from RiderProfile if it exists"""
        try:
            from core.models import User
            user = User.objects.filter(email=obj.email).first()
            if user and hasattr(user, 'rider_profile'):
                return user.rider_profile.total_deliveries or 0
        except:
            pass
        return 0

    def get_bank_details(self, obj):
        """Get bank details from RiderBank if it exists"""
        try:
            from core.models import User
            user = User.objects.filter(email=obj.email).first()
            if user and hasattr(user, 'rider_bank'):
                bank = user.rider_bank
                return {
                    'account_holder_name': bank.account_holder_name,
                    'account_number': bank.account_number,
                    'ifsc_code': bank.ifsc_code,
                    'bank_name': bank.bank_name,
                    'verified': bank.verified
                }
        except:
            pass
        return None


# Keep legacy serializer available for internal use if needed
class RiderProfileSerializer(serializers.ModelSerializer):
    rider_name = serializers.CharField(source='rider.name', read_only=True)
    rider_email = serializers.CharField(source='rider.email', read_only=True)

    class Meta:
        model = RiderProfile
        fields = ['id', 'rider', 'rider_name', 'rider_email', 'vehicle_type',
                  'vehicle_number', 'status', 'rating', 'total_deliveries', 'wallet_balance', 'city',
                  'is_online', 'created_at']



class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item_name', 'quantity', 'price', 'subtotal', 'customizations']


class OrderSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    rider_name = serializers.CharField(source='rider.name', read_only=True, allow_null=True)
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_id', 'user', 'user_name', 'restaurant', 'restaurant_name',
                  'rider', 'rider_name', 'status', 'payment_status', 'payment_method',
                  'total', 'subtotal', 'delivery_fee', 'discount', 'tax', 
                  'placed_at', 'delivered_at', 'items', 'delivery_address']



class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'title', 'image', 'link', 'is_active', 'order', 'created_at']


class CommissionSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    
    class Meta:
        model = Commission
        fields = ['id', 'restaurant', 'restaurant_name', 'rate', 'effective_from',
                  'effective_until', 'created_at']


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'description', 'discount_type', 'discount_value',
                  'min_order_amount', 'max_discount', 'valid_from', 'valid_until',
                  'usage_limit', 'used_count', 'is_active', 'created_at']


class WalletTransactionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='wallet.user.name', read_only=True)
    
    class Meta:
        model = WalletTransaction
        fields = ['id', 'wallet', 'user_name', 'transaction_type', 'amount',
                  'source', 'description', 'order', 'balance_after', 'created_at']


class RestaurantEarningsSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    order_id_str = serializers.CharField(source='order.order_id', read_only=True)
    
    class Meta:
        model = RestaurantEarnings
        fields = ['id', 'restaurant', 'restaurant_name', 'order', 'order_id_str',
                  'order_total', 'commission', 'net_amount', 'date', 'created_at']



class SitePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = SitePolicy
        fields = ['id', 'title', 'slug', 'policy_type', 'content', 'is_active',
                  'updated_at', 'created_at']


class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = ['id', 'key', 'value', 'description', 'updated_at', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'user_name', 'restaurant', 'restaurant_name', 
                  'order', 'rating', 'comment', 'created_at']


class MenuItemSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = MenuItem
        fields = ['id', 'restaurant', 'restaurant_name', 'name', 'description', 
                  'image', 'price', 'veg_type', 'category', 'category_name',
                  'is_available', 'preparation_time', 'rating', 'total_orders', 
                  'created_at', 'updated_at']

