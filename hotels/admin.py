from django.contrib import admin
from .models import Hotel, Booking, City, HotelChain, Amenity, Room, RoomType, HotelImage, RoomImage


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'is_popular', 'created_at']
    list_filter = ['country', 'is_popular']
    search_fields = ['name', 'country']
    ordering = ['country', 'name']


@admin.register(HotelChain)
class HotelChainAdmin(admin.ModelAdmin):
    list_display = ['name', 'star_rating', 'website']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_premium']
    list_filter = ['category', 'is_premium']
    search_fields = ['name']
    ordering = ['category', 'name']


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'max_occupancy', 'bed_type']
    list_filter = ['name', 'bed_type']
    search_fields = ['display_name']
    ordering = ['name']


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'star_rating', 'base_price', 'guest_rating', 'is_featured']
    list_filter = ['city', 'star_rating', 'is_featured', 'is_verified']
    search_fields = ['name', 'city__name']
    filter_horizontal = ['amenities']
    ordering = ['name']
    readonly_fields = ['slug', 'guest_rating', 'total_reviews']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'hotel', 'room_type', 'base_price', 'is_available']
    list_filter = ['hotel', 'room_type', 'is_available']
    search_fields = ['room_number', 'hotel__name']
    filter_horizontal = ['amenities']
    ordering = ['hotel', 'room_number']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'guest_name', 'hotel', 'check_in', 'check_out', 'total_guests', 'total_amount', 'status')
    list_filter = ('status', 'check_in', 'check_out', 'hotel')
    search_fields = ('guest_name', 'guest_email', 'hotel__name', 'booking_reference')
    ordering = ('-created_at',)
    readonly_fields = ('booking_reference', 'confirmation_code', 'total_amount')


@admin.register(HotelImage)
class HotelImageAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'caption', 'is_primary', 'order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['hotel__name', 'caption']
    ordering = ['hotel', 'order']


@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ['room', 'caption', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['room__hotel__name', 'room__room_number', 'caption']
    ordering = ['room', 'order']