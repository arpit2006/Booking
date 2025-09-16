from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
import uuid
from typing import TYPE_CHECKING

# Optional imports for geocoding
try:
    from geopy.geocoders import Nominatim  # type: ignore
    from geopy.exc import GeocoderTimedOut  # type: ignore
except ImportError:
    Nominatim = None
    GeocoderTimedOut = Exception

if TYPE_CHECKING:
    from reviews.models import Review

# Type ignore for Django model field defaults and ORM methods
# pyright: reportArgumentType=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportReturnType=false
# pyright: reportOperatorIssue=false
# pyright: reportCallIssue=false


class City(models.Model):
    """Model for cities where hotels are located"""
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    is_popular = models.BooleanField(default=False)
    image = models.ImageField(upload_to='cities/', blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"{self.name}, {self.country}"
    
    class Meta:
        verbose_name_plural = "Cities"
        unique_together = ['name', 'country']
        ordering = ['country', 'name']


class HotelChain(models.Model):
    """Model for hotel chains/brands"""
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='hotel_chains/', blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    star_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    
    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = "Hotel Chain"
        verbose_name_plural = "Hotel Chains"


class Amenity(models.Model):
    """Model for hotel amenities"""
    AMENITY_CATEGORIES = [
        ('general', 'General'),
        ('room', 'Room'),
        ('bathroom', 'Bathroom'),
        ('entertainment', 'Entertainment'),
        ('connectivity', 'Connectivity'),
        ('food_drink', 'Food & Drink'),
        ('wellness', 'Wellness & Spa'),
        ('business', 'Business'),
        ('family', 'Family'),
        ('accessibility', 'Accessibility'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=AMENITY_CATEGORIES)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class", blank=True)
    description = models.TextField(blank=True)
    is_premium = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name_plural = "Amenities"
        ordering = ['category', 'name']
class Hotel(models.Model):
    """Enhanced Hotel model with comprehensive features"""
    HOTEL_TYPES = [
        ('hotel', 'Hotel'),
        ('resort', 'Resort'),
        ('motel', 'Motel'),
        ('hostel', 'Hostel'),
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('guesthouse', 'Guest House'),
        ('bnb', 'Bed & Breakfast'),
        ('boutique', 'Boutique Hotel'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(unique=True, blank=True)
    hotel_type = models.CharField(max_length=20, choices=HOTEL_TYPES, default='hotel')
    chain = models.ForeignKey(HotelChain, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Location
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    address = models.TextField()
    postal_code = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Contact Information
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Description and Features
    description = models.TextField()
    short_description = models.CharField(max_length=300, help_text="Brief description for search results")
    amenities = models.ManyToManyField(Amenity, blank=True)
    
    # Ratings and Reviews
    star_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Official hotel star rating"
    )
    guest_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Pricing
    base_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Base price per night"
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Images
    main_image = models.ImageField(upload_to='hotels/main/', blank=True)
    
    # Business Information
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_hotels'
    )
    license_number = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    
    # Policies
    check_in_time = models.TimeField(default='15:00')
    check_out_time = models.TimeField(default='11:00')
    cancellation_policy = models.TextField(blank=True)
    pet_policy = models.TextField(blank=True)
    smoking_policy = models.CharField(
        max_length=20,
        choices=[
            ('no_smoking', 'No Smoking'),
            ('smoking_rooms', 'Smoking Rooms Available'),
            ('designated_areas', 'Designated Smoking Areas'),
        ],
        default='no_smoking'
    )
    
    # Status and Verification
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return f"{self.name} - {self.city}"
    
    def get_absolute_url(self):
        return reverse('hotel_detail', kwargs={'slug': self.slug})
    
    @property
    def available_rooms_count(self):
        return self.rooms.filter(is_available=True).count()
    
    @property
    def lowest_price(self):
        """Get the lowest room price for this hotel"""
        lowest = self.rooms.filter(is_available=True).aggregate(
            models.Min('price_per_night')
        )['price_per_night__min']
        return lowest or self.base_price
    
    @property
    def rating_percentage(self):
        """Convert rating to percentage for star display"""
        return (self.guest_rating / 5) * 100
    
    def update_rating(self):
        """Update guest rating based on reviews"""
        from reviews.models import Review
        reviews = Review.objects.filter(hotel=self)
        if reviews.exists():
            avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.guest_rating = round(avg_rating, 2)
            self.total_reviews = reviews.count()
            self.save(update_fields=['guest_rating', 'total_reviews'])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(f"{self.name}-{self.city.name}")
            slug = base_slug
            counter = 1
            while Hotel.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Auto-geocode if coordinates not provided
        if not self.latitude or not self.longitude:
            try:
                if Nominatim:
                    geolocator = Nominatim(user_agent="booking_mvp")
                    location = geolocator.geocode(f"{self.address}, {self.city}")
                    if location:
                        self.latitude = location.latitude
                        self.longitude = location.longitude
            except GeocoderTimedOut:
                pass
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-is_featured', '-guest_rating', 'name']
        indexes = [
            models.Index(fields=['city', 'is_active']),
            models.Index(fields=['guest_rating']),
            models.Index(fields=['created_at']),
        ]


class HotelImage(models.Model):
    """Additional images for hotels"""
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='hotels/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.hotel.name} - Image {self.id}"
    
    class Meta:
        ordering = ['order', 'created_at']


class RoomType(models.Model):
    """Enhanced room type model"""
    ROOM_TYPES = [
        ('single', 'Single Room'),
        ('double', 'Double Room'),
        ('twin', 'Twin Room'),
        ('triple', 'Triple Room'),
        ('quad', 'Quad Room'),
        ('suite', 'Suite'),
        ('junior_suite', 'Junior Suite'),
        ('presidential_suite', 'Presidential Suite'),
        ('deluxe', 'Deluxe Room'),
        ('standard', 'Standard Room'),
        ('superior', 'Superior Room'),
        ('family', 'Family Room'),
        ('studio', 'Studio'),
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('penthouse', 'Penthouse'),
    ]
    
    BED_TYPES = [
        ('single', 'Single Bed'),
        ('double', 'Double Bed'),
        ('queen', 'Queen Bed'),
        ('king', 'King Bed'),
        ('twin', 'Twin Beds'),
        ('sofa_bed', 'Sofa Bed'),
        ('bunk_bed', 'Bunk Bed'),
    ]
    
    name = models.CharField(max_length=50, choices=ROOM_TYPES)
    display_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    max_occupancy = models.PositiveIntegerField(default=2)
    max_adults = models.PositiveIntegerField(default=2)
    max_children = models.PositiveIntegerField(default=0)
    bed_type = models.CharField(max_length=20, choices=BED_TYPES, default='double')
    bed_count = models.PositiveIntegerField(default=1)
    room_size = models.PositiveIntegerField(null=True, blank=True, help_text="Size in square meters")
    has_balcony = models.BooleanField(default=False)
    has_sea_view = models.BooleanField(default=False)
    has_city_view = models.BooleanField(default=False)
    has_garden_view = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return self.display_name or self.get_name_display()
    
    class Meta:
        verbose_name = "Room Type"
        verbose_name_plural = "Room Types"
        ordering = ['name']


class Room(models.Model):
    """Enhanced room model with comprehensive features"""
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=20)
    floor = models.PositiveIntegerField(null=True, blank=True)
    
    # Pricing
    base_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    weekend_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True, blank=True
    )
    peak_season_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True, blank=True
    )
    
    # Room Features
    amenities = models.ManyToManyField(Amenity, blank=True)
    special_features = models.TextField(blank=True)
    
    # Availability
    is_available = models.BooleanField(default=True)
    is_accessible = models.BooleanField(default=False)
    is_smoking_allowed = models.BooleanField(default=False)
    
    # Room Images
    main_image = models.ImageField(upload_to='rooms/main/', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.hotel.name} - Room {self.room_number} ({self.room_type})"
    
    def get_price_for_date(self, date):
        """Get dynamic pricing based on date"""
        # Weekend pricing (Friday, Saturday)
        if date.weekday() in [4, 5] and self.weekend_price:
            return self.weekend_price
        
        # Peak season pricing (customize based on your needs)
        # This is a simplified example
        if date.month in [6, 7, 8, 12] and self.peak_season_price:
            return self.peak_season_price
        
        return self.base_price
    
    @property
    def current_price(self):
        """Get current price based on today's date"""
        from django.utils import timezone
        return self.get_price_for_date(timezone.now().date())
    
    def is_available_for_dates(self, check_in, check_out):
        """Check if room is available for given date range"""
        if not self.is_available:
            return False
        
        # Check for existing bookings
        conflicting_bookings = self.bookings.filter(
            models.Q(check_in__lt=check_out) & models.Q(check_out__gt=check_in),
            status__in=['confirmed', 'checked_in']
        )
        return not conflicting_bookings.exists()
    
    class Meta:
        unique_together = ['hotel', 'room_number']
        ordering = ['hotel', 'floor', 'room_number']
        indexes = [
            models.Index(fields=['hotel', 'is_available']),
            models.Index(fields=['room_type']),
        ]


class RoomImage(models.Model):
    """Additional images for rooms"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='rooms/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.room} - Image {self.id}"
    
    class Meta:
        ordering = ['order', 'created_at']


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Booking(models.Model):
    """Enhanced booking model with comprehensive features"""
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('refunded', 'Refunded'),
    ]
    
    GUEST_TYPES = [
        ('adult', 'Adult'),
        ('child', 'Child'),
        ('infant', 'Infant'),
    ]
    
    # Booking Identification
    booking_reference = models.CharField(max_length=20, unique=True, editable=False)
    confirmation_code = models.CharField(max_length=8, unique=True, editable=False, default='DEFAULT')
    
    # Guest Information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    guest_name = models.CharField(max_length=200, default='Guest')
    guest_email = models.EmailField(default='guest@example.com')
    guest_phone = models.CharField(max_length=20)
    
    # Booking Details
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')
    rooms = models.ManyToManyField(Room, through='BookingRoom')
    check_in = models.DateField(db_index=True)
    check_out = models.DateField(db_index=True)
    
    # Guest Count
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    infants = models.PositiveIntegerField(default=0)
    
    # Pricing
    room_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Booking Status and Tracking
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    special_requests = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True, help_text="For hotel staff only")
    
    # Check-in/out tracking
    actual_check_in = models.DateTimeField(null=True, blank=True)
    actual_check_out = models.DateTimeField(null=True, blank=True)
    early_check_in_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    late_check_out_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Cancellation
    cancellation_date = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    cancellation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Source tracking
    booking_source = models.CharField(
        max_length=20,
        choices=[
            ('website', 'Website'),
            ('mobile_app', 'Mobile App'),
            ('phone', 'Phone'),
            ('email', 'Email'),
            ('walk_in', 'Walk-in'),
            ('third_party', 'Third Party'),
        ],
        default='website'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.booking_reference} - {self.guest_name} @ {self.hotel}"
    
    def get_absolute_url(self):
        return reverse('booking_detail', kwargs={'reference': self.booking_reference})
    
    @property
    def nights_count(self):
        return (self.check_out - self.check_in).days
    
    @property
    def total_guests(self):
        return self.adults + self.children + self.infants
    
    @property
    def is_active(self):
        return self.status in ['pending', 'confirmed', 'checked_in']
    
    @property
    def can_cancel(self):
        """Check if booking can be cancelled"""
        if self.status in ['cancelled', 'checked_out', 'no_show']:
            return False
        
        # Check cancellation policy (simplified)
        from django.utils import timezone
        time_until_checkin = self.check_in - timezone.now().date()
        return time_until_checkin.days >= 1
    
    @property
    def can_modify(self):
        """Check if booking can be modified"""
        return self.status in ['pending', 'confirmed'] and self.can_cancel
    
    def calculate_total(self):
        """Calculate total booking amount"""
        self.total_amount = (
            self.room_total + 
            self.tax_amount + 
            self.service_fee + 
            self.early_check_in_fee + 
            self.late_check_out_fee - 
            self.discount_amount
        )
        return self.total_amount
    
    def generate_confirmation_code(self):
        """Generate a simple confirmation code"""
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            # Generate unique booking reference
            import uuid
            self.booking_reference = f"BK{str(uuid.uuid4()).replace('-', '').upper()[:8]}"
        
        if not self.confirmation_code:
            self.confirmation_code = self.generate_confirmation_code()
        
        # Auto-calculate total if not set
        if not self.total_amount:
            self.calculate_total()
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['hotel', 'check_in']),
            models.Index(fields=['status', 'check_in']),
            models.Index(fields=['booking_reference']),
        ]


class BookingRoom(models.Model):
    """Through model for booking-room relationship"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    room_rate = models.DecimalField(max_digits=10, decimal_places=2)
    nights = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.booking.booking_reference} - {self.room}"
    
    class Meta:
        unique_together = ['booking', 'room']


class Payment(models.Model):
    """Enhanced payment model with comprehensive features"""
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]
    
    PAYMENT_METHOD = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('wallet', 'Digital Wallet'),
    ]
    
    # Payment Identification
    payment_id = models.CharField(max_length=50, unique=True, editable=False)
    transaction_id = models.CharField(max_length=100, blank=True)
    
    # Booking Reference
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    
    # Payment Details
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment for {self.booking.booking_reference} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.payment_id:
            import uuid
            self.payment_id = f"PAY{str(uuid.uuid4()).replace('-', '').upper()[:10]}"
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']