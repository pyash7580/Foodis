from django.contrib import admin
from .models import RestaurantProfile, RestaurantEarnings, OrderStatusUpdate


@admin.register(RestaurantProfile)
class RestaurantProfileAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'gst_number', 'fssai_license', 'created_at']
    search_fields = ['restaurant__name', 'gst_number', 'fssai_license']


@admin.register(RestaurantEarnings)
class RestaurantEarningsAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'order', 'order_total', 'commission', 'net_amount', 'date']
    list_filter = ['date', 'restaurant']
    search_fields = ['restaurant__name', 'order__order_id']


@admin.register(OrderStatusUpdate)
class OrderStatusUpdateAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'updated_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_id']

