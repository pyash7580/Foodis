from django.contrib import admin
from .models import Rider, OrderAssignment, Earning, Payout

@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ['phone', 'full_name', 'city', 'status', 'wallet_balance', 'is_active', 'created_at']
    list_filter = ['status', 'is_active', 'city', 'created_at']
    search_fields = ['phone', 'full_name', 'city']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(OrderAssignment)
class OrderAssignmentAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'rider', 'status', 'assigned_at', 'updated_at']
    list_filter = ['status', 'assigned_at']
    search_fields = ['order_id', 'rider__phone', 'rider__full_name']

@admin.register(Earning)
class EarningAdmin(admin.ModelAdmin):
    list_display = ['rider', 'order_id', 'amount', 'transaction_type', 'timestamp']
    list_filter = ['transaction_type', 'timestamp']
    search_fields = ['rider__phone', 'order_id']

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ['rider', 'amount', 'status', 'requested_at', 'paid_at']
    list_filter = ['status', 'requested_at']
    search_fields = ['rider__phone']
