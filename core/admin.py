from django.contrib import admin
from .models import User, Address, OTP


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['phone', 'name', 'email', 'role', 'is_active', 'is_verified', 'created_at']
    list_filter = ['role', 'is_active', 'is_verified', 'created_at']
    search_fields = ['phone', 'name', 'email']
    readonly_fields = ['created_at', 'updated_at', 'last_login']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'label', 'city', 'is_default', 'created_at']
    list_filter = ['city', 'is_default', 'created_at']
    search_fields = ['user__phone', 'user__name', 'address_line1', 'city']


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['phone', 'otp_code', 'is_verified', 'created_at', 'expires_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['phone']
    readonly_fields = ['created_at', 'expires_at']

