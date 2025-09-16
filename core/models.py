from django.db import models
from django.core.cache import cache
from django.utils import timezone


class SiteSettings(models.Model):
    """Site-wide settings and configuration"""
    site_name = models.CharField(max_length=100, default='BookingMVP')
    site_tagline = models.CharField(max_length=200, default='Your Perfect Stay Awaits')
    site_description = models.TextField(default='Book amazing hotels worldwide')
    
    # Contact Information
    contact_email = models.EmailField(default='contact@bookingmvp.com')
    contact_phone = models.CharField(max_length=20, blank=True)
    support_email = models.EmailField(default='support@bookingmvp.com')
    
    # Business Settings
    default_currency = models.CharField(max_length=3, default='USD')
    default_tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.1000)
    service_fee_percentage = models.DecimalField(max_digits=5, decimal_places=4, default=0.0500)
    
    # Features
    enable_reviews = models.BooleanField(default=True)
    enable_coupons = models.BooleanField(default=True)
    enable_wishlists = models.BooleanField(default=True)
    require_email_verification = models.BooleanField(default=True)
    
    # Social Media
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Maintenance
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return self.site_name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Clear cache when settings are updated
        cache.delete('site_settings')
    
    @classmethod
    def get_settings(cls):
        """Get cached site settings"""
        settings = cache.get('site_settings')
        if not settings:
            settings, created = cls.objects.get_or_create(pk=1)
            cache.set('site_settings', settings, 3600)  # Cache for 1 hour
        return settings
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'


class EmailTemplate(models.Model):
    """Email templates for notifications"""
    TEMPLATE_TYPES = [
        ('booking_confirmation', 'Booking Confirmation'),
        ('booking_cancellation', 'Booking Cancellation'),
        ('payment_confirmation', 'Payment Confirmation'),
        ('welcome_email', 'Welcome Email'),
        ('password_reset', 'Password Reset'),
        ('review_request', 'Review Request'),
    ]
    
    name = models.CharField(max_length=50, choices=TEMPLATE_TYPES, unique=True)
    subject = models.CharField(max_length=200)
    content = models.TextField(help_text='Use {{variable}} for dynamic content')
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_name_display()} Template"
    
    class Meta:
        ordering = ['name']
