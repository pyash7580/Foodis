from django.db import models
from django.core.validators import RegexValidator

class Rider(models.Model):
    """
    Delivery Partner (Rider) core model.
    Mobile number is the unique identifier.
    """
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    STATUS_CHOICES = [
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
        ('BUSY', 'Busy'),
    ]
    
    phone = models.CharField(validators=[phone_regex], max_length=17, unique=True, primary_key=True)
    full_name = models.CharField(max_length=255)
    
    # Status
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OFFLINE')
    is_online = models.BooleanField(default=False) # Keep for compatibility, sync in save()
    
    # Order Reference (Decoupled)
    current_order_id = models.IntegerField(null=True, blank=True)
    
    # Financials
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Location Info
    city = models.CharField(max_length=100, default='Mehsana')
    current_latitude = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    CITY_CENTERS = {
        'Mehsana': {'lat': 23.5880, 'lng': 72.3693},
        'Himmatnagar': {'lat': 23.5937, 'lng': 72.9691},
    }

    class Meta:
        verbose_name = "Delivery Partner"
        verbose_name_plural = "Delivery Partners"

    def save(self, *args, **kwargs):
        # Normalize city name
        from core.city_utils import normalize_city_name
        self.city = normalize_city_name(self.city)
        
        # Sync is_online for compatibility
        self.is_online = (self.status == 'ONLINE')
        
        # Force location to city center if online (Mock Location Enforcement)
        if self.is_online and self.city in self.CITY_CENTERS:
            center = self.CITY_CENTERS[self.city]
            self.current_latitude = center['lat']
            self.current_longitude = center['lng']
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.phone})"


class OrderAssignment(models.Model):
    """
    Tracks the lifecycle of an order assigned to a rider.
    """
    STATUS_CHOICES = [
        ('ASSIGNED', 'Assigned'),
        ('ACCEPTED', 'Accepted'),
        ('PICKED_UP', 'Picked Up'),
        ('ON_THE_WAY', 'On the way'),
        ('DELIVERED', 'Delivered'),
        ('REJECTED', 'Rejected'),
    ]

    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='assignments')
    order_id = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ASSIGNED')
    
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-assigned_at']

    def __str__(self):
        return f"Order {self.order_id} - {self.rider.phone} ({self.status})"


class Earning(models.Model):
    """
    Earning records for specific orders or incentives.
    """
    TRANSACTION_TYPES = [
        ('DELIVERY', 'Delivery Fee'),
        ('INCENTIVE', 'Incentive'),
        ('ADJUSTMENT', 'Adjustment'),
    ]

    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='earnings')
    order_id = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='DELIVERY')
    
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"₹{self.amount} - {self.rider.phone} ({self.transaction_type})"
class Payout(models.Model):
    """
    Rider payout request and status.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('REJECTED', 'Rejected'),
    ]

    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    requested_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"Payout ₹{self.amount} - {self.rider.phone} ({self.status})"
