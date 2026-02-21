from rest_framework import serializers
from .models import (
    Category, Restaurant, MenuItem, MenuItemCustomization, CustomizationOption,
    Cart, CartItem, Order, OrderItem, Coupon, Wallet, WalletTransaction, Review,
    SavedPaymentMethod, FavouriteRestaurant, FavouriteMenuItem
)
from core.models import Address
from core.serializers import SmartImageField
from geopy.distance import distance


class CategorySerializer(serializers.ModelSerializer):
    image = SmartImageField(required=False, allow_null=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'is_active']


class CustomizationOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomizationOption
        fields = ['id', 'name', 'price', 'is_available']


class MenuItemCustomizationSerializer(serializers.ModelSerializer):
    options = CustomizationOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = MenuItemCustomization
        fields = ['id', 'name', 'is_required', 'max_selections', 'options']


class MenuItemSerializer(serializers.ModelSerializer):
    image = SmartImageField(required=False, allow_null=True)
    customizations = MenuItemCustomizationSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    is_favourite = serializers.SerializerMethodField()

    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    restaurant_slug = serializers.CharField(source='restaurant.slug', read_only=True)
    restaurant_city = serializers.CharField(source='restaurant.city', read_only=True)
    image_url = serializers.ReadOnlyField(source='get_image_url')

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'image', 'image_url', 'price', 'veg_type',
                  'category', 'category_name', 'is_available', 'preparation_time',
                  'rating', 'total_orders', 'customizations', 'is_favourite',
                  'restaurant', 'restaurant_name', 'restaurant_slug', 'restaurant_city']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-load all favorite menu items in a single query (not per-item)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            from .models import FavouriteMenuItem
            # Load all favorited menu item IDs for this user in ONE query
            fav_item_ids = set(
                FavouriteMenuItem.objects.filter(user=request.user)
                .values_list('menu_item_id', flat=True)
            )
            self.context['fav_menu_items'] = fav_item_ids
        else:
            self.context['fav_menu_items'] = set()

    def get_is_favourite(self, obj):
        # Use pre-loaded set instead of querying for each menu item
        fav_menu_items = self.context.get('fav_menu_items', set())
        return obj.id in fav_menu_items


class RestaurantSerializer(serializers.ModelSerializer):
    image = SmartImageField(required=False, allow_null=True)
    cover_image = SmartImageField(required=False, allow_null=True)
    image_url = serializers.ReadOnlyField(source='get_image_url')
    cover_image_url = serializers.ReadOnlyField(source='get_cover_image_url')
    distance = serializers.SerializerMethodField()
    menu_items_count = serializers.SerializerMethodField()
    cuisine_types = serializers.SerializerMethodField()

    is_favourite = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'slug', 'description', 'cuisine', 'image', 'cover_image', 'image_url', 'cover_image_url',
                  'phone', 'email', 'address', 'city', 'state', 'pincode',
                  'latitude', 'longitude', 'rating', 'total_ratings',
                  'delivery_time', 'delivery_fee', 'min_order_amount',
                  'is_veg', 'is_active', 'distance', 'menu_items_count', 'cuisine_types', 'is_favourite']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-load all favorite restaurants in a single query (not per-item)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            from .models import FavouriteRestaurant
            # Load all favorited restaurant IDs for this user in ONE query
            fav_rest_ids = set(
                FavouriteRestaurant.objects.filter(user=request.user)
                .values_list('restaurant_id', flat=True)
            )
            self.context['fav_restaurants'] = fav_rest_ids
        else:
            self.context['fav_restaurants'] = set()

    def get_is_favourite(self, obj):
        # Use pre-loaded set instead of querying for each restaurant
        fav_restaurants = self.context.get('fav_restaurants', set())
        return obj.id in fav_restaurants

    def get_cuisine_types(self, obj):
        # Avoid N+1 query: use prefetched menu_items if available
        menu_items = obj.menu_items.all()  # Uses prefetched cache if available
        categories = set()
        for item in menu_items:
            if item.category and item.category.name:
                categories.add(item.category.name)
        return list(categories)[:3]

    def get_menu_items_count(self, obj):
        # Use annotated count if available, otherwise fallback to count()
        if hasattr(obj, 'menu_items_count_cached'):
            return obj.menu_items_count_cached
        return obj.menu_items.count()

    def get_distance(self, obj):
        # Only calculate distance if explicitly requested in query params
        # Most of the distance filtering is done in get_queryset already
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user_lat = request.query_params.get('latitude')
            user_lng = request.query_params.get('longitude')
            if user_lat and user_lng:
                try:
                    user_location = (float(user_lat), float(user_lng))
                    restaurant_location = (float(obj.latitude), float(obj.longitude))
                    dist = distance(user_location, restaurant_location).km
                    return round(dist, 2)
                except:
                    pass
        return None


class RestaurantDetailSerializer(RestaurantSerializer):
    menu_items = MenuItemSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField()
    
    class Meta(RestaurantSerializer.Meta):
        fields = RestaurantSerializer.Meta.fields + ['menu_items', 'reviews']
    
    def get_reviews(self, obj):
        reviews = obj.reviews.all()[:10]
        return ReviewSerializer(reviews, many=True).data


class CartItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'menu_item', 'menu_item_id', 'quantity', 'customizations', 'subtotal']
    
    def validate_menu_item_id(self, value):
        if not MenuItem.objects.filter(id=value, is_available=True).exists():
            raise serializers.ValidationError("Menu item not available")
        return value


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    restaurant = RestaurantSerializer(read_only=True)
    restaurant_id = serializers.IntegerField(write_only=True, required=False)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'restaurant', 'restaurant_id', 'items', 'total', 'created_at', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'quantity', 'price', 'customizations', 'subtotal']


from rider_legacy.serializers import RiderReviewSerializer
from django.contrib.auth import get_user_model
User = get_user_model()

class PublicRiderSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.SerializerMethodField()
    vehicle_type = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'avatar', 'vehicle_number', 'vehicle_type', 'rating']

    def get_vehicle_number(self, obj):
        if hasattr(obj, 'rider_profile'):
            return obj.rider_profile.vehicle_number
        return None

    def get_vehicle_type(self, obj):
        if hasattr(obj, 'rider_profile'):
            return obj.rider_profile.vehicle_type
        return None

    def get_rating(self, obj):
        if hasattr(obj, 'rider_profile'):
            return obj.rider_profile.rating
        return None


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    restaurant = RestaurantSerializer(read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    rider = PublicRiderSerializer(read_only=True)
    rider_name = serializers.CharField(source='rider.name', read_only=True, allow_null=True)
    has_restaurant_review = serializers.SerializerMethodField()
    has_rider_review = serializers.SerializerMethodField()
    restaurant_review_details = serializers.SerializerMethodField()
    rider_review_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'order_id', 'user', 'user_name', 'restaurant', 'rider', 'rider_name',
                  'delivery_address', 'delivery_latitude', 'delivery_longitude',
                  'delivery_phone', 'delivery_instructions', 'subtotal', 'delivery_fee',
                  'discount', 'tax', 'total', 'coupon', 'status', 'payment_method',
                  'payment_status', 'items', 'pickup_otp', 'delivery_otp', 
                  'placed_at', 'confirmed_at', 'preparing_at',
                  'ready_at', 'picked_up_at', 'delivered_at', 'rider_latitude',
                  'rider_longitude', 'estimated_delivery_time',
                  'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature',
                  'has_restaurant_review', 'has_rider_review', 
                  'restaurant_review_details', 'rider_review_details']

    def get_has_restaurant_review(self, obj):
        try:
            return obj.review.exists()
        except:
            return False

    def get_has_rider_review(self, obj):
        return hasattr(obj, 'rider_review')

    def get_restaurant_review_details(self, obj):
        if hasattr(obj, 'review'):
            review_obj = obj.review.first()
            if review_obj:
                return ReviewSerializer(review_obj).data
        return None

    def get_rider_review_details(self, obj):
        if hasattr(obj, 'rider_review'):
            return RiderReviewSerializer(obj.rider_review).data
        return None


class CouponSerializer(serializers.ModelSerializer):
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'description', 'discount_type', 'discount_value',
                  'min_order_amount', 'max_discount', 'valid_from', 'valid_until',
                  'usage_limit', 'used_count', 'is_active', 'is_valid']
    
    def get_is_valid(self, obj):
        order_amount = self.context.get('order_amount', 0)
        return obj.is_valid(order_amount)


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ['id', 'transaction_type', 'amount', 'source', 'description',
                  'order', 'balance_after', 'created_at']


class WalletSerializer(serializers.ModelSerializer):
    transactions = WalletTransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Wallet
        fields = ['id', 'balance', 'transactions', 'created_at', 'updated_at']


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'user_name', 'restaurant', 'order', 'rating',
                  'comment', 'created_at', 'updated_at']
        read_only_fields = ['user']


class SavedPaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedPaymentMethod
        fields = ['id', 'method_type', 'card_brand', 'card_last4', 'card_expiry', 'upi_id', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']


class FavouriteRestaurantSerializer(serializers.ModelSerializer):
    restaurant_details = RestaurantSerializer(source='restaurant', read_only=True)
    
    class Meta:
        model = FavouriteRestaurant
        fields = ['id', 'restaurant', 'restaurant_details', 'created_at']


class FavouriteMenuItemSerializer(serializers.ModelSerializer):
    menu_item_details = MenuItemSerializer(source='menu_item', read_only=True)
    
    class Meta:
        model = FavouriteMenuItem
        fields = ['id', 'menu_item', 'menu_item_details', 'created_at']
