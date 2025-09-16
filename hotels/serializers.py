from rest_framework import serializers
from .models import Hotel, Booking, City, Amenity, Room, HotelImage
from django.contrib.auth import get_user_model
from datetime import date

# Type ignore for Django ORM and DRF issues
# pyright: reportAttributeAccessIssue=false
# pyright: reportIncompatibleMethodOverride=false

User = get_user_model()


class CitySerializer(serializers.ModelSerializer):
    """Serializer for City model"""
    class Meta:
        model = City
        fields = ['id', 'name', 'country', 'is_popular']
        read_only_fields = ['id']


class AmenitySerializer(serializers.ModelSerializer):
    """Serializer for Amenity model"""
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'icon', 'category']
        read_only_fields = ['id']


class HotelListSerializer(serializers.ModelSerializer):
    """Simplified serializer for hotel listings"""
    city = CitySerializer(read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'slug', 'city', 'address', 'description',
            'base_price', 'star_rating', 'guest_rating', 'is_featured',
            'main_image', 'amenities', 'average_rating', 'review_count'
        ]
        read_only_fields = ['id', 'slug']
    
    def get_average_rating(self, obj):
        return obj.guest_rating or 4.0
    
    def get_review_count(self, obj):
        # Mock review count since we don't have reviews model integrated
        return 50


class HotelDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual hotel views"""
    city = CitySerializer(read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    
    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'slug', 'city', 'address', 'description',
            'base_price', 'star_rating', 'guest_rating', 'is_featured',
            'main_image', 'amenities', 'phone', 'email', 'website',
            'check_in_time', 'check_out_time', 'cancellation_policy',
            'average_rating', 'review_count', 'images', 'latitude', 'longitude'
        ]
        read_only_fields = ['id', 'slug']
    
    def get_average_rating(self, obj):
        return obj.guest_rating or 4.0
    
    def get_review_count(self, obj):
        return 50
    
    def get_images(self, obj):
        # Mock images since we don't have images model
        return []


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class BookingListSerializer(serializers.ModelSerializer):
    """Simplified serializer for booking listings"""
    hotel = HotelListSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    nights = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'booking_reference', 'hotel', 'user', 'check_in', 'check_out',
            'adults', 'children', 'infants', 'total_amount', 'status', 'created_at', 'nights'
        ]
        read_only_fields = ['id', 'booking_reference', 'created_at']
    
    def get_nights(self, obj):
        return (obj.check_out - obj.check_in).days


class BookingDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual booking views"""
    hotel = HotelDetailSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    nights = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'booking_reference', 'hotel', 'user', 'check_in', 'check_out',
            'adults', 'children', 'infants', 'total_amount', 'status', 'created_at', 'updated_at', 'nights'
        ]
        read_only_fields = ['id', 'booking_reference', 'created_at', 'updated_at']
    
    def get_nights(self, obj):
        return (obj.check_out - obj.check_in).days


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new bookings"""
    hotel = serializers.PrimaryKeyRelatedField(queryset=Hotel.objects.all())
    nights = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'hotel', 'check_in', 'check_out', 'adults', 'children', 'infants', 'nights'
        ]
    
    def get_nights(self, obj):
        if obj.check_in and obj.check_out:
            return (obj.check_out - obj.check_in).days
        return 0
    
    def validate(self, data):
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        adults = data.get('adults', 1)
        
        # Validate check_out > check_in
        if check_out <= check_in:
            raise serializers.ValidationError("Check-out date must be after check-in date.")
        
        # Validate adults > 0
        if adults <= 0:
            raise serializers.ValidationError("Number of adults must be greater than 0.")
        
        # Validate dates are not in the past
        if check_in < date.today():
            raise serializers.ValidationError("Check-in date cannot be in the past.")
        
        return data
    
    def create(self, validated_data):
        # Auto-calculate total_amount
        hotel = validated_data['hotel']
        check_in = validated_data['check_in']
        check_out = validated_data['check_out']
        nights = (check_out - check_in).days
        
        # Get user from request context
        user = self.context['request'].user
        
        # Calculate total amount
        total_amount = nights * hotel.base_price
        
        # Create booking
        booking = Booking.objects.create(
            user=user,
            hotel=hotel,
            check_in=check_in,
            check_out=check_out,
            adults=validated_data.get('adults', 1),
            children=validated_data.get('children', 0),
            infants=validated_data.get('infants', 0),
            guest_name=user.get_full_name() or user.username,
            guest_email=user.email,
            total_amount=total_amount,
            status='confirmed'
        )
        
        # Send confirmation emails
        try:
            from .emails import send_booking_confirmation_email, send_hotel_owner_notification
            send_booking_confirmation_email(booking)
            send_hotel_owner_notification(booking, 'new_booking')
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Failed to send booking emails: {str(e)}')
        
        return booking