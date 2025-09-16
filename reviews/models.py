from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# Type ignore for Django model field defaults and ORM methods
# pyright: reportArgumentType=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportReturnType=false
# pyright: reportOperatorIssue=false
# pyright: reportCallIssue=false


class Review(models.Model):
    """Hotel and booking reviews by guests"""
    REVIEW_TYPES = [
        ('stay', 'Stay Review'),
        ('service', 'Service Review'),
        ('facility', 'Facility Review'),
    ]
    
    # Review Details
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    hotel = models.ForeignKey('hotels.Hotel', on_delete=models.CASCADE, related_name='reviews')
    booking = models.ForeignKey('hotels.Booking', on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    
    # Review Content
    title = models.CharField(max_length=200)
    content = models.TextField()
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Detailed Ratings
    cleanliness_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    service_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    location_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    value_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    amenities_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    
    # Review Metadata
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPES, default='stay')
    is_verified = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='moderated_reviews'
    )
    moderation_notes = models.TextField(blank=True)
    
    # Helpfulness
    helpful_count = models.PositiveIntegerField(default=0)
    not_helpful_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    stay_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.hotel.name} ({self.rating}/5)"
    
    @property
    def average_detailed_rating(self):
        """Calculate average of detailed ratings"""
        ratings = [r for r in [
            self.cleanliness_rating,
            self.service_rating,
            self.location_rating,
            self.value_rating,
            self.amenities_rating
        ] if r is not None]
        
        return sum(ratings) / len(ratings) if ratings else self.rating
    
    @property
    def helpfulness_ratio(self):
        """Calculate helpfulness ratio"""
        total_votes = self.helpful_count + self.not_helpful_count
        return (self.helpful_count / total_votes * 100) if total_votes > 0 else 0
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'booking']  # One review per booking per user
        indexes = [
            models.Index(fields=['hotel', 'is_approved']),
            models.Index(fields=['rating']),
            models.Index(fields=['created_at']),
        ]


class ReviewHelpfulness(models.Model):
    """Track review helpfulness votes"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpfulness_votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_helpful = models.BooleanField()  # True for helpful, False for not helpful
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        vote_type = "helpful" if self.is_helpful else "not helpful"
        return f"{self.user.username} - {self.review.title} - {vote_type}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update review helpfulness counts
        self.review.helpful_count = self.review.helpfulness_votes.filter(is_helpful=True).count()
        self.review.not_helpful_count = self.review.helpfulness_votes.filter(is_helpful=False).count()
        self.review.save(update_fields=['helpful_count', 'not_helpful_count'])
    
    class Meta:
        unique_together = ['review', 'user']  # One vote per user per review


class ReviewImage(models.Model):
    """Images attached to reviews"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='reviews/images/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.review.title}"
    
    class Meta:
        ordering = ['order', 'created_at']


class ReviewResponse(models.Model):
    """Hotel owner responses to reviews"""
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='response')
    responder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_responses'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Response to {self.review.title}"
    
    class Meta:
        ordering = ['-created_at']
