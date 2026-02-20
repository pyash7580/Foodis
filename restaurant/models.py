from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal
from client.models import Restaurant, Order, MenuItem

User = get_user_model()


class RestaurantProfile(models.Model):
    """Extended Restaurant Profile"""
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE, related_name='profile')
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    pan_number = models.CharField(max_length=50, blank=True, null=True)
    fssai_license = models.CharField(max_length=50, blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'restaurant_profiles'
        verbose_name = 'Restaurant Profile'
        verbose_name_plural = 'Restaurant Profiles'
    
    def __str__(self):
        return f"{self.restaurant.name} - Profile"


class RestaurantEarnings(models.Model):
    """Restaurant Earnings Tracking"""
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='earnings')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='restaurant_earnings')
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'restaurant_earnings'
        verbose_name = 'Restaurant Earning'
        verbose_name_plural = 'Restaurant Earnings'
        indexes = [
            models.Index(fields=['restaurant', 'date']),
        ]
    
    def __str__(self):
        return f"{self.restaurant.name} - ₹{self.net_amount} - {self.date}"


class OrderStatusUpdate(models.Model):
    """Order Status Update History"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_updates')
    status = models.CharField(max_length=20)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_status_updates'
        verbose_name = 'Order Status Update'
        verbose_name_plural = 'Order Status Updates'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.order_id} - {self.status}"

