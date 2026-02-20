from django.contrib import admin
from .models import RiderProfile, RiderEarnings, RiderLocation


@admin.register(RiderProfile)
class RiderProfileAdmin(admin.ModelAdmin):
    list_display = ['rider', 'vehicle_type', 'vehicle_number', 'is_online', 'status', 'rating', 'total_deliveries']
    list_filter = ['status', 'is_online', 'vehicle_type', 'created_at']
    search_fields = ['rider__phone', 'rider__name', 'vehicle_number', 'license_number']


@admin.register(RiderEarnings)
class RiderEarningsAdmin(admin.ModelAdmin):
    list_display = ['rider', 'order', 'delivery_fee', 'tip', 'total_earning', 'date']
    list_filter = ['date', 'rider']
    search_fields = ['rider__phone', 'order__order_id']


@admin.register(RiderLocation)
class RiderLocationAdmin(admin.ModelAdmin):
    list_display = ['rider', 'latitude', 'longitude', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['rider__phone']
    readonly_fields = ['timestamp']

