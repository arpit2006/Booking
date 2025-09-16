from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Extended User model with additional profile fields"""
    
    # Profile fields
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    # Address fields
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Preferences
    newsletter_subscription = models.BooleanField(default=False)
    preferred_currency = models.CharField(
        max_length=3,
        choices=[
            ('USD', 'US Dollar'),
            ('EUR', 'Euro'),
            ('GBP', 'British Pound'),
            ('INR', 'Indian Rupee'),
        ],
        default='USD'
    )
    
    # Account type
    USER_TYPES = [
        ('customer', 'Customer'),
        ('hotel_owner', 'Hotel Owner'),
        ('admin', 'Admin'),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_full_name() or self.email})"
    
    @property
    def full_address(self):
        """Return formatted full address"""
        address_parts = [self.address_line_1, self.address_line_2, self.city, self.state, self.postal_code, self.country]
        return ', '.join([part for part in address_parts if part])
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class UserProfile(models.Model):
    """Additional profile information for users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True)
    
    # Travel preferences
    favorite_destinations = models.TextField(blank=True, help_text="Comma-separated list")
    travel_style = models.CharField(
        max_length=20,
        choices=[
            ('budget', 'Budget Traveler'),
            ('luxury', 'Luxury Traveler'),
            ('business', 'Business Traveler'),
            ('family', 'Family Traveler'),
            ('adventure', 'Adventure Traveler'),
        ],
        blank=True
    )
    
    # Social media
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    
    # Verification status
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    identity_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    class Meta:
        db_table = 'accounts_userprofile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
