from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()


class Banner(models.Model):
    """Banner Model for Homepage"""
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='banners/')
    link = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'banners'
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title


class Commission(models.Model):
    """Commission Settings"""
    restaurant = models.ForeignKey('client.Restaurant', on_delete=models.CASCADE, related_name='commissions')
    rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    effective_from = models.DateTimeField()
    effective_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'commissions'
        verbose_name = 'Commission'
        verbose_name_plural = 'Commissions'
    
    def __str__(self):
        return f"{self.restaurant.name} - {self.rate}%"


class SitePolicy(models.Model):
    """Site Policies (Terms, Privacy, etc.)"""
    POLICY_TYPES = [
        ('TERMS', 'Terms of Service'),
        ('PRIVACY', 'Privacy Policy'),
        ('REFUND', 'Refund Policy'),
        ('SHIPPING', 'Shipping Policy'),
        ('CANCELLATION', 'Cancellation Policy'),
    ]
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPES)
    content = models.TextField(help_text="Policy content in HTML/Markdown format")
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'site_policies'
        verbose_name = 'Site Policy'
        verbose_name_plural = 'Site Policies'
        ordering = ['policy_type']
    
    def __str__(self):
        return self.title


class SystemSettings(models.Model):
    """System-wide Settings"""
    key = models.CharField(max_length=100, unique=True, 
                          help_text="Setting key (e.g., 'default_commission_rate')")
    value = models.TextField(help_text="Setting value (JSON compatible)")
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'system_settings'
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
        ordering = ['key']
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"


class AdminLog(models.Model):
    """Log of Admin Actions"""
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='admin_logs')
    action = models.CharField(max_length=255)
    target_model = models.CharField(max_length=100, blank=True, null=True)
    target_id = models.CharField(max_length=100, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admin_logs'
        verbose_name = 'Admin Log'
        verbose_name_plural = 'Admin Logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.admin.name if self.admin else 'System'}: {self.action} at {self.timestamp}"
