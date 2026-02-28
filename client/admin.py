from django.contrib import admin
from .models import (
    Category, Restaurant, MenuItem, MenuItemCustomization, CustomizationOption,
    Cart, CartItem, Order, OrderItem, Coupon, Wallet, WalletTransaction, Review,
    OrderOTP
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'city', 'status', 'rating', 'is_active', 'created_at']
    list_filter = ['status', 'is_active', 'city', 'created_at']
    search_fields = ['name', 'owner__email', 'city']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'price', 'veg_type', 'is_available', 'rating']
    list_filter = ['restaurant', 'veg_type', 'is_available', 'category']
    search_fields = ['name', 'restaurant__name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'restaurant', 'status', 'payment_status', 'total', 'placed_at']
    list_filter = ['status', 'payment_status', 'payment_method', 'placed_at']
    search_fields = ['order_id', 'user__email', 'restaurant__name']
    readonly_fields = ['order_id', 'placed_at', 'confirmed_at', 'preparing_at', 
                      'ready_at', 'picked_up_at', 'delivered_at', 'cancelled_at']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'is_active', 'used_count', 'usage_limit']
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_until']
    search_fields = ['code']


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'created_at', 'updated_at']
    search_fields = ['user__email', 'user__name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'restaurant', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__email', 'restaurant__name']


@admin.register(OrderOTP)
class OrderOTPAdmin(admin.ModelAdmin):
    list_display = ['order', 'otp_type', 'is_used', 'attempt_count', 'expires_at', 'created_at']
    list_filter = ['otp_type', 'is_used', 'created_at']
    search_fields = ['order__order_id', 'order__related_user__email']
    readonly_fields = ['otp_hash', 'created_at', 'expires_at']

