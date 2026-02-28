from django.contrib import admin
from .models import User, Address, OTP


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'role', 'is_active', 'is_verified', 'email_verified', 'created_at']
    list_filter = ['role', 'is_active', 'is_verified', 'email_verified', 'created_at']
    search_fields = ['email', 'name']
    readonly_fields = ['created_at', 'updated_at', 'last_login']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'label', 'city', 'is_default', 'created_at']
    list_filter = ['city', 'is_default', 'created_at']
    search_fields = ['user__email', 'user__name', 'address_line1', 'city']


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['email', 'otp_code', 'is_verified', 'created_at', 'expires_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['email']
    readonly_fields = ['created_at', 'expires_at']

