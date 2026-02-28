from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = get_user_model()
from core.models import City


class RiderProfile(models.Model):
    """Rider Profile Model"""
    VEHICLE_CHOICES = [
        ('BIKE', 'Bike'),
        ('SCOOTER', 'Scooter'),
        ('CYCLE', 'Cycle'),
    ]
    
    STATUS_CHOICES = [
        ('NEW', 'New Registration'),
        ('ONBOARDING', 'Onboarding in Progress'),
        ('UNDER_REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SUSPENDED', 'Suspended'),
        ('BLOCKED', 'Blocked'),
    ]
    
    # Core Relationships
    rider = models.OneToOneField(User, on_delete=models.CASCADE, related_name='rider_profile')
    
    # 📌 ONE RIDER = ONE ACTIVE ORDER
    # Using OneToOne to strictly enforce single active order at database level if possible, 
    # but since order history exists, we stick to a field that points to the *current* active one.
    current_order = models.OneToOneField(
        'client.Order', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_rider_profile'
    )
    
    # Identity (Mobile is Truth)
    # mobile_number = models.CharField(max_length=15, unique=True, null=True, blank=True, help_text="Single Source of Truth") # REMOVED
    
    # Profile Details
    profile_photo = models.ImageField(upload_to='rider_profiles/', blank=True, null=True)
    city = models.CharField(max_length=100, default='Himmatnagar')
    city_id = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='rider_profiles')
    
    # Vehicle & Legal
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES, default='BIKE')
    vehicle_number = models.CharField(max_length=50, blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    aadhar_number = models.CharField(max_length=12, blank=True, null=True)
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    
    # State Engine
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    onboarding_step = models.IntegerField(default=0) # 0-6
    is_onboarding_complete = models.BooleanField(default=False)
    
    # Real-time Status
    is_online = models.BooleanField(default=False)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    # Stats
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    total_deliveries = models.IntegerField(default=0)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rider_profiles'
        verbose_name = 'Rider Profile'
        verbose_name_plural = 'Rider Profiles'
    
    def __str__(self):
        return f"{self.rider.email} - {self.status}"

    CITY_CENTERS = {
        'Mehsana': {'lat': 23.5880, 'lng': 72.3693},
        'Himmatnagar': {'lat': 23.5937, 'lng': 72.9691},
    }

    def save(self, *args, **kwargs):
        # mobile_number sync removed
            
        # Auto-sync city_id from city string if possible
        if self.city and not self.city_id:
            try:
                # Direct match
                self.city_id = City.objects.filter(name__iexact=self.city.strip()).first()
                if not self.city_id:
                    # Handle variations
                    variations = {
                        'Himmat Nagar': 'Himmatnagar',
                        'Mehsana ': 'Mehsana',
                    }
                    mapped_name = variations.get(self.city.strip())
                    if mapped_name:
                        self.city_id = City.objects.filter(name__iexact=mapped_name).first()
            except Exception as e:
                print(f"Error auto-syncing city_id: {e}")
            
        # Force location to city center if online (Mock Location Enforcement for Testing)
        # Use city_id first, then fallback to city string
        city_name = self.city
        if self.city_id:
            city_name = self.city_id.name

        if self.is_online and city_name in self.CITY_CENTERS:
            center = self.CITY_CENTERS[city_name]
            self.current_latitude = center['lat']
            self.current_longitude = center['lng']
            
        super().save(*args, **kwargs)


class RiderDocument(models.Model):
    """Rider Documents for Verification"""
    DOCUMENT_TYPES = [
        ('AADHAR_FRONT', 'Aadhaar Card Front'),
        ('AADHAR_BACK', 'Aadhaar Card Back'),
        ('LICENSE', 'Driving License'),
        ('SELFIE_WITH_VEHICLE', 'Selfie with Vehicle'),
    ]
    
    rider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rider_documents')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.ImageField(upload_to='rider_documents/')
    verified = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rider_documents'
        verbose_name = 'Rider Document'
        verbose_name_plural = 'Rider Documents'

    def __str__(self):
        return f"{self.rider.name} - {self.document_type}"


class RiderBank(models.Model):
    """Rider Bank Details"""
    rider = models.OneToOneField(User, on_delete=models.CASCADE, related_name='rider_bank')
    account_holder_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    ifsc_code = models.CharField(max_length=11)
    bank_name = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rider_bank_details'
        verbose_name = 'Rider Bank Detail'
        verbose_name_plural = 'Rider Bank Details'

    def __str__(self):
        return f"{self.rider.name} - {self.bank_name}"


class RiderEarnings(models.Model):
    """Rider Earnings Tracking"""
    rider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rider_earnings')
    order = models.ForeignKey('client.Order', on_delete=models.CASCADE, related_name='rider_earnings')
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    tip = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_earning = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rider_earnings'
        verbose_name = 'Rider Earning'
        verbose_name_plural = 'Rider Earnings'
        indexes = [
            models.Index(fields=['rider', 'date']),
        ]
    
    def __str__(self):
        return f"{self.rider.name} - ₹{self.total_earning} - {self.date}"


class RiderLocation(models.Model):
    """Rider Location Tracking"""
    rider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rider_locations'
        verbose_name = 'Rider Location'
        verbose_name_plural = 'Rider Locations'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['rider', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.rider.name} - {self.timestamp}"


class RiderReview(models.Model):
    """Review for Riders"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rider_reviews_given')
    rider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rider_reviews_received')
    order = models.OneToOneField('client.Order', on_delete=models.CASCADE, related_name='rider_review')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rider_reviews'
        verbose_name = 'Rider Review'
        verbose_name_plural = 'Rider Reviews'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.name} -> {self.rider.name} ({self.rating}⭐)"

class RiderNotification(models.Model):
    """Rider Notifications and Alerts"""
    NOTIFICATION_TYPES = [
        ('ORDER', 'New Order Alert'),
        ('INCENTIVE', 'Incentive Milestone'),
        ('SYSTEM', 'System Message'),
        ('PAYOUT', 'Payment/Wallet Update'),
    ]
    
    rider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rider_notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='SYSTEM')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rider_notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rider.name} - {self.title}"


class IncentiveScheme(models.Model):
    """Incentive Schemes (Daily targets, Peak hours)"""
    SCHEME_TYPES = [
        ('DAILY_ORDER_TARGET', 'Daily Order Target'),
        ('PEAK_HOUR_BONUS', 'Peak Hour Bonus'),
        ('REFERRAL', 'Referral Bonus'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    scheme_type = models.CharField(max_length=50, choices=SCHEME_TYPES)
    target_count = models.IntegerField(help_text="Target number of orders")
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    start_time = models.TimeField(null=True, blank=True, help_text="For peak hour bonuses")
    end_time = models.TimeField(null=True, blank=True, help_text="For peak hour bonuses")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rider_incentive_schemes'

    def __str__(self):
        return self.title


class RiderIncentiveProgress(models.Model):
    """Tracks rider progress towards incentives"""
    rider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incentive_progress')
    scheme = models.ForeignKey(IncentiveScheme, on_delete=models.CASCADE)
    current_count = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    earned_at = models.DateTimeField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'rider_incentive_progress'
        unique_together = ['rider', 'scheme', 'date']

    def __str__(self):
        return f"{self.rider.name} - {self.scheme.title} ({self.current_count}/{self.scheme.target_count})"
