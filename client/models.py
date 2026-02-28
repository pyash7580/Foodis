from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
from core.models import City

User = get_user_model()


class Category(models.Model):
    """Food Categories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Restaurant(models.Model):
    """Restaurant Model"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SUSPENDED', 'Suspended'),
    ]
    
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    cuisine = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='restaurants/logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='restaurants/covers/', blank=True, null=True)
    # phone = models.CharField(max_length=17, blank=True, null=True)  # REMOVED
    email = models.EmailField(null=True, blank=True, default='')  # Primary auth identifier
    password = models.CharField(max_length=255, null=True, blank=True)  # Hashed password for email+password auth
    address = models.TextField()
    city = models.CharField(max_length=100)
    city_id = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='restaurants')
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_ratings = models.IntegerField(default=0)
    delivery_time = models.IntegerField(default=30)  # minutes
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_veg = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)  # percentage
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'restaurants'
        verbose_name = 'Restaurant'
        verbose_name_plural = 'Restaurants'
        indexes = [
            models.Index(fields=['status', 'is_active'], name='idx_restaurant_status_active'),
            models.Index(fields=['city'], name='idx_restaurant_city'),
            models.Index(fields=['latitude', 'longitude'], name='idx_restaurant_coordinates'),
        ]
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto-sync city_id from city string if missing
        if self.city:
            from core.city_utils import normalize_city_name
            self.city = normalize_city_name(self.city)
            
            if not self.city_id:
                try:
                    from core.models import City
                    self.city_id = City.objects.filter(name__iexact=self.city).first()
                except Exception as e:
                    print(f"Error auto-syncing restaurant city_id: {e}")
        
        super().save(*args, **kwargs)

    @property
    def get_image_url(self):
        if self.image:
            return self.image.url
        return None

    @property
    def get_cover_image_url(self):
        if self.cover_image:
            return self.cover_image.url
        return None


class MenuItem(models.Model):
    """Menu Item Model"""
    VEG_CHOICES = [
        ('VEG', 'Vegetarian'),
        ('NON_VEG', 'Non-Vegetarian'),
        ('EGG', 'Contains Egg'),
    ]
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='menu_items/dishes/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    veg_type = models.CharField(max_length=10, choices=VEG_CHOICES, default='VEG')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='menu_items')
    is_available = models.BooleanField(default=True, db_index=True)
    preparation_time = models.IntegerField(default=15)  # minutes
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_orders = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'menu_items'
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
        indexes = [
            models.Index(fields=['restaurant', 'is_available']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"

    @property
    def get_image_url(self):
        if self.image:
            return self.image.url
        return None


class MenuItemCustomization(models.Model):
    """Menu Item Customization Options"""
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='customizations')
    name = models.CharField(max_length=100)  # e.g., "Size", "Toppings"
    is_required = models.BooleanField(default=False)
    max_selections = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'menu_item_customizations'
        verbose_name = 'Menu Item Customization'
        verbose_name_plural = 'Menu Item Customizations'
    
    def __str__(self):
        return f"{self.menu_item.name} - {self.name}"


class CustomizationOption(models.Model):
    """Customization Option Values"""
    customization = models.ForeignKey(MenuItemCustomization, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_available = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'customization_options'
        verbose_name = 'Customization Option'
        verbose_name_plural = 'Customization Options'
    
    def __str__(self):
        return f"{self.customization.name} - {self.name}"


class Cart(models.Model):
    """Shopping Cart Model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        unique_together = ['user', 'restaurant']
    
    def __str__(self):
        return f"{self.user.name} - {self.restaurant.name}"
    
    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    """Cart Item Model"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)], default=1)
    customizations = models.JSONField(default=dict, blank=True)  # Store selected customization options
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cart_items'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'menu_item', 'customizations']
    
    def __str__(self):
        return f"{self.cart.user.name} - {self.menu_item.name} x{self.quantity}"
    
    @property
    def subtotal(self):
        base_price = self.menu_item.price * self.quantity
        customization_price = Decimal('0.00')
        if self.customizations:
            # Calculate customization prices
            for cust_id, option_ids in self.customizations.items():
                if isinstance(option_ids, list):
                    for option_id in option_ids:
                        try:
                            option = CustomizationOption.objects.get(id=option_id)
                            customization_price += option.price * self.quantity
                        except:
                            pass
        return base_price + customization_price


class Coupon(models.Model):
    """Coupon Model"""
    TYPE_CHOICES = [
        ('PERCENTAGE', 'Percentage'),
        ('FIXED', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    discount_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='PERCENTAGE')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    usage_limit = models.IntegerField(default=1000)
    used_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'coupons'
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
    
    def __str__(self):
        return self.code
    
    def is_valid(self, order_amount):
        from django.utils import timezone
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        if order_amount < self.min_order_amount:
            return False
        if self.used_count >= self.usage_limit:
            return False
        return True
    
    def calculate_discount(self, order_amount):
        if not self.is_valid(order_amount):
            return Decimal('0.00')
        
        if self.discount_type == 'PERCENTAGE':
            discount = (order_amount * self.discount_value) / 100
            if self.max_discount:
                discount = min(discount, self.max_discount)
        else:
            discount = min(self.discount_value, order_amount)
        
        return discount


class Order(models.Model):
    """Order Model"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PREPARING', 'Preparing'),
        ('READY', 'Ready for Pickup'),
        ('ASSIGNED', 'Assigned to Rider'),
        ('PICKED_UP', 'Picked Up'),
        ('ON_THE_WAY', 'On the Way'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('UPI', 'UPI'),
        ('CARD', 'Credit/Debit Card'),
        ('NETBANKING', 'Net Banking'),
        ('WALLET', 'Wallet'),
        ('COD', 'Cash on Delivery'),
        ('RAZORPAY', 'Razorpay'), # Keep for compatibility, but prefer specific ones
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    order_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    city_id = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    rider = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='delivery_orders', limit_choices_to={'role': 'RIDER'})
    
    # Address
    delivery_address = models.TextField()
    delivery_latitude = models.DecimalField(max_digits=18, decimal_places=6)
    delivery_longitude = models.DecimalField(max_digits=18, decimal_places=6)
    # delivery_phone = models.CharField(max_length=17) # REMOVED
    delivery_instructions = models.TextField(blank=True, null=True)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=5.00) # Fixed ₹5
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Coupon
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    cancellation_reason = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    
    # Split Payment Tracking
    wallet_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    online_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    refund_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    placed_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    preparing_at = models.DateTimeField(null=True, blank=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking
    rider_latitude = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    rider_longitude = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    estimated_delivery_time = models.IntegerField(null=True, blank=True)  # minutes
    
    # Verification OTPs
    pickup_otp = models.CharField(max_length=6, null=True, blank=True)
    delivery_otp = models.CharField(max_length=6, null=True, blank=True)
    
    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['restaurant', 'status']),
            models.Index(fields=['rider', 'status']),
            models.Index(fields=['order_id']),
        ]
        ordering = ['-placed_at']
    
    def __str__(self):
        return f"Order {self.order_id}"
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            import uuid
            self.order_id = f"ORD{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Order Item Model"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    customizations = models.JSONField(default=dict, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    def __str__(self):
        return f"{self.order.order_id} - {self.menu_item.name} x{self.quantity}"


class Wallet(models.Model):
    """User Wallet Model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.00'))])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'wallets'
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
    
    def save(self, *args, **kwargs):
        if self.balance < 0:
            self.balance = Decimal('0.00')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.name} - ₹{self.balance}"


class WalletTransaction(models.Model):
    """Wallet Transaction Model"""
    TYPE_CHOICES = [
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),
    ]
    
    SOURCE_CHOICES = [
        ('REFUND', 'Refund'),
        ('RECHARGE', 'Recharge'),
        ('ORDER_PAYMENT', 'Order Payment'),
        ('CASHBACK', 'Cashback'),
        ('ADMIN', 'Admin Adjustment'),
    ]
    
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    description = models.TextField(blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='wallet_transactions')
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'wallet_transactions'
        verbose_name = 'Wallet Transaction'
        verbose_name_plural = 'Wallet Transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.wallet.user.name} - {self.transaction_type} - ₹{self.amount}"


class Review(models.Model):
    """Review Model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='review', null=True, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reviews'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ['user', 'order']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.name} - {self.restaurant.name} - {self.rating}⭐"


class SavedPaymentMethod(models.Model):
    """Saved Payment Methods (Cards/UPI)"""
    METHOD_TYPES = [
        ('CARD', 'Card'),
        ('UPI', 'UPI ID'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_payments')
    method_type = models.CharField(max_length=10, choices=METHOD_TYPES)
    
    # For Cards
    card_brand = models.CharField(max_length=50, blank=True, null=True) # Visa, Mastercard, etc.
    card_last4 = models.CharField(max_length=4, blank=True, null=True)
    card_expiry = models.CharField(max_length=10, blank=True, null=True) # MM/YYYY
    
    # For UPI
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'saved_payment_methods'
        verbose_name = 'Saved Payment Method'
        verbose_name_plural = 'Saved Payment Methods'

    def __str__(self):
        return f"{self.user.name} - {self.method_type}"


class FavouriteRestaurant(models.Model):
    """User Favourite Restaurants"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourite_restaurants')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_favourite_restaurants'
        unique_together = ['user', 'restaurant']
        verbose_name = 'Favourite Restaurant'
        verbose_name_plural = 'Favourite Restaurants'
        indexes = [
            models.Index(fields=['user'], name='idx_fav_rest_user'),
            models.Index(fields=['user', 'restaurant'], name='idx_fav_rest_user_restaurant'),
        ]

    def __str__(self):
        return f"{self.user.name} ❤️ {self.restaurant.name}"


class FavouriteMenuItem(models.Model):
    """User Favourite Menu Items"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourite_menu_items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_favourite_menu_items'
        unique_together = ['user', 'menu_item']
        verbose_name = 'Favourite Menu Item'
        verbose_name_plural = 'Favourite Menu Items'
        indexes = [
            models.Index(fields=['user'], name='idx_fav_item_user'),
            models.Index(fields=['user', 'menu_item'], name='idx_fav_item_user_menuitem'),
        ]

    def __str__(self):
        return f"{self.user.name} ❤️ {self.menu_item.name}"


class OrderOTP(models.Model):
    OTP_TYPE_CHOICES = [
        ('PICKUP', 'Pickup Verification'),
        ('DELIVERY', 'Delivery Verification'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_otps')
    otp_hash = models.CharField(max_length=128)  # Storing hash, not plain OTP
    otp_type = models.CharField(max_length=10, choices=OTP_TYPE_CHOICES)
    related_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="User who verifies this OTP (e.g. Rider)")
    
    is_used = models.BooleanField(default=False)
    attempt_count = models.IntegerField(default=0)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'order_otps'
        verbose_name = 'Order OTP'
        verbose_name_plural = 'Order OTPs'
        indexes = [
            models.Index(fields=['order', 'otp_type', 'is_used']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"OTP {self.otp_type} for {self.order.order_id}"
