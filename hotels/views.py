from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.urls import reverse
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Hotel, Booking, City, Amenity
from .serializers import (
    HotelListSerializer, HotelDetailSerializer, BookingListSerializer,
    BookingDetailSerializer, BookingCreateSerializer, CitySerializer,
    AmenitySerializer
)
from .emails import send_booking_confirmation_email, send_hotel_owner_notification
from datetime import date, datetime
import uuid
import decimal

# Type ignore for Django ORM and DRF issues
# pyright: reportAttributeAccessIssue=false
# pyright: reportIncompatibleMethodOverride=false
# pyright: reportOperatorIssue=false


def home_view(request):
    """Homepage with search and featured content"""
    # Get featured hotels
    featured_hotels = Hotel.objects.filter(is_featured=True, is_active=True)[:6]
    
    # Get popular destinations
    popular_destinations = City.objects.filter(is_popular=True)[:6]
    
    context = {
        'featured_hotels': featured_hotels,
        'popular_destinations': popular_destinations,
    }
    return render(request, 'home.html', context)


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset for cities"""
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country', 'is_popular']
    search_fields = ['name', 'country']
    ordering_fields = ['name', 'country']
    ordering = ['name']


class AmenityViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset for amenities"""
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name']
    ordering = ['category', 'name']


class HotelViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset for hotels with advanced filtering and search"""
    queryset = Hotel.objects.filter(is_active=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'city': ['exact'],
        'star_rating': ['exact', 'gte', 'lte'],
        'base_price': ['gte', 'lte'],
        'guest_rating': ['gte'],
        'is_featured': ['exact'],
    }
    search_fields = ['name', 'description', 'address', 'city__name']
    ordering_fields = ['name', 'base_price', 'guest_rating', 'star_rating']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HotelDetailSerializer
        return HotelListSerializer
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured hotels"""
        featured_hotels = self.queryset.filter(is_featured=True)[:6]
        serializer = self.get_serializer(featured_hotels, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced hotel search with custom parameters"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Custom filters
        location = request.query_params.get('location')
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        guests = request.query_params.get('guests')
        
        if location:
            queryset = queryset.filter(
                Q(name__icontains=location) |
                Q(city__name__icontains=location) |
                Q(address__icontains=location)
            )
        
        # Add availability check logic here if needed
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    """API viewset for bookings with full CRUD operations"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        'status': ['exact'],
        'check_in': ['gte', 'lte'],
        'check_out': ['gte', 'lte'],
        'created_at': ['gte', 'lte'],
    }
    ordering_fields = ['created_at', 'check_in', 'check_out', 'total_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter bookings by current user"""
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        elif self.action == 'retrieve':
            return BookingDetailSerializer
        return BookingListSerializer
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking"""
        booking = self.get_object()
        
        # Check if booking can be cancelled
        if booking.status == 'cancelled':
            return Response(
                {'error': 'Booking is already cancelled'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if booking.check_in <= date.today():
            return Response(
                {'error': 'Cannot cancel booking for past dates'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cancel the booking
        booking.status = 'cancelled'
        booking.save()
        
        # Send cancellation email
        try:
            from .emails import send_booking_cancellation_email, send_hotel_owner_notification
            send_booking_cancellation_email(booking)
            send_hotel_owner_notification(booking, 'booking_cancelled')
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Failed to send cancellation emails: {str(e)}')
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming bookings for the current user"""
        upcoming_bookings = self.get_queryset().filter(
            check_in__gte=date.today(),
            status__in=['confirmed', 'pending']
        )
        serializer = self.get_serializer(upcoming_bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get booking history for the current user"""
        past_bookings = self.get_queryset().filter(
            check_out__lt=date.today()
        )
        serializer = self.get_serializer(past_bookings, many=True)
        return Response(serializer.data)


def hotel_list_view(request):
    """Hotel search and listing with filters"""
    hotels = Hotel.objects.filter(is_active=True)
    total_hotels = hotels.count()
    
    # Search filters
    location = request.GET.get('location')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    guests = request.GET.get('guests')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    amenities = request.GET.getlist('amenities')
    stars = request.GET.getlist('stars')
    sort = request.GET.get('sort', 'name')
    
    if location:
        hotels = hotels.filter(
            Q(name__icontains=location) |
            Q(city__name__icontains=location) |
            Q(address__icontains=location)
        )
    
    if min_price:
        try:
            hotels = hotels.filter(price_per_night__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            hotels = hotels.filter(price_per_night__lte=float(max_price))
        except ValueError:
            pass
    
    if amenities:
        for amenity in amenities:
            if amenity == 'wifi':
                # Filter by description or amenities containing wifi
                hotels = hotels.filter(Q(description__icontains='wifi') | Q(description__icontains='internet'))
            elif amenity == 'pool':
                hotels = hotels.filter(description__icontains='pool')
            elif amenity == 'spa':
                hotels = hotels.filter(description__icontains='spa')
            elif amenity == 'restaurant':
                hotels = hotels.filter(description__icontains='restaurant')
            elif amenity == 'gym':
                hotels = hotels.filter(Q(description__icontains='gym') | Q(description__icontains='fitness'))
    
    if stars:
        star_filters = Q()
        for star in stars:
            try:
                star_filters |= Q(star_rating=int(star))
            except ValueError:
                pass
        if star_filters:
            hotels = hotels.filter(star_filters)
    
    # Sorting
    if sort == 'price_low':
        hotels = hotels.order_by('price_per_night')
    elif sort == 'price_high':
        hotels = hotels.order_by('-price_per_night')
    elif sort == 'rating':
        hotels = hotels.order_by('-guest_rating')
    else:
        hotels = hotels.order_by('name')
    
    # Add calculated fields
    for hotel in hotels:
        hotel.average_rating = hotel.guest_rating or 4.0
        hotel.review_count = 50  # Mock review count
        if not hasattr(hotel, 'amenities'):
            hotel.amenities = type('MockAmenities', (), {
                'all': lambda: [],
                'count': lambda: 0
            })()
    
    # Pagination
    paginator = Paginator(hotels, 12)  # Show 12 hotels per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'hotels': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_hotels': total_hotels,
    }
    return render(request, 'hotels/hotel_list.html', context)


def hotel_detail_view(request, slug):
    """Hotel detail page"""
    hotel = get_object_or_404(Hotel, slug=slug, is_active=True)
    
    # Add calculated fields for template compatibility
    hotel.average_rating = hotel.guest_rating or 4.0
    hotel.review_count = 50  # Mock review count
    
    # Mock amenities if not available
    if not hasattr(hotel, 'amenities'):
        hotel.amenities = type('MockAmenities', (), {
            'all': lambda: [],
            'count': lambda: 0
        })()
    
    # Mock reviews
    mock_reviews = []
    for i in range(3):
        review = type('MockReview', (), {
            'user': type('MockUser', (), {
                'first_name': ['John', 'Jane', 'Mike'][i],
                'last_name': ['Doe', 'Smith', 'Johnson'][i],
                'get_full_name': lambda: f'{["John", "Jane", "Mike"][i]} {["Doe", "Smith", "Johnson"][i]}',
                'username': ['john_doe', 'jane_smith', 'mike_j'][i]
            })(),
            'rating': [5, 4, 5][i],
            'comment': [
                'Amazing hotel with excellent service and beautiful rooms!',
                'Great location and friendly staff. Would definitely stay again.',
                'Perfect for a weekend getaway. Highly recommended!'
            ][i],
            'created_at': date.today()
        })()
        mock_reviews.append(review)
    
    hotel.reviews = type('MockReviews', (), {
        'all': lambda: mock_reviews,
        'count': lambda: len(mock_reviews)
    })()
    
    # Mock images
    if not hasattr(hotel, 'images'):
        hotel.images = type('MockImages', (), {
            'all': lambda: []
        })()
    
    context = {
        'hotel': hotel,
    }
    return render(request, 'hotels/hotel_detail.html', context)


@login_required
def book_hotel_view(request, slug):
    """Handle hotel booking"""
    hotel = get_object_or_404(Hotel, slug=slug, is_active=True)
    
    if request.method == 'POST':
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        guests = request.POST.get('guests')
        room_type = request.POST.get('room_type', 'standard')
        
        # Basic validation
        if not all([check_in, check_out, guests]):
            messages.error(request, 'All fields are required.')
            return redirect('hotels:hotel_detail', slug=slug)
        
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
            guests_count = int(guests)
            
            # Validate dates and guests
            if check_out_date <= check_in_date:
                messages.error(request, 'Check-out date must be after check-in date.')
                return redirect('hotels:hotel_detail', slug=slug)
            elif guests_count <= 0:
                messages.error(request, 'Number of guests must be greater than 0.')
                return redirect('hotels:hotel_detail', slug=slug)
            elif check_in_date < date.today():
                messages.error(request, 'Check-in date cannot be in the past.')
                return redirect('hotels:hotel_detail', slug=slug)
            
            # Calculate pricing
            nights = (check_out_date - check_in_date).days
            base_price = hotel.price_per_night * nights
            
            # Room upgrade costs
            room_upgrade_costs = {
                'standard': 0,
                'deluxe': 20 * nights,
                'suite': 50 * nights
            }
            room_upgrade_cost = room_upgrade_costs.get(room_type, 0)
            
            subtotal = base_price + room_upgrade_cost
            taxes = decimal.Decimal(subtotal * decimal.Decimal('0.12'))  # 12% tax
            total_amount = subtotal + taxes
            
            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                hotel=hotel,
                check_in=check_in_date,
                check_out=check_out_date,
                guests=guests_count,
                booking_id=str(uuid.uuid4())[:8].upper(),
                total_amount=total_amount,
                status='confirmed'
            )
            
            # Add additional booking details
            booking.nights = nights
            booking.subtotal = base_price
            booking.room_type = room_type
            booking.room_upgrade_cost = room_upgrade_cost
            booking.taxes = taxes
            booking.payment_method = 'Credit Card'  # Mock payment method
            
            # Send confirmation emails
            try:
                send_booking_confirmation_email(booking)
                send_hotel_owner_notification(booking, 'new_booking')
            except Exception as e:
                # Log error but don't fail the booking
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Failed to send booking emails: {str(e)}')
            
            return redirect('hotels:booking_confirmation', booking_id=booking.booking_id)
            
        except ValueError as e:
            messages.error(request, 'Invalid date format or number of guests.')
            return redirect('hotels:hotel_detail', slug=slug)
        except Exception as e:
            messages.error(request, 'An error occurred while processing your booking. Please try again.')
            return redirect('hotels:hotel_detail', slug=slug)
    
    return redirect('hotels:hotel_detail', slug=slug)


@login_required
def booking_confirmation_view(request, booking_id):
    """Display booking confirmation"""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    
    # Add calculated fields if not present
    if not hasattr(booking, 'nights'):
        booking.nights = (booking.check_out - booking.check_in).days
    if not hasattr(booking, 'subtotal'):
        booking.subtotal = booking.hotel.price_per_night * booking.nights
    if not hasattr(booking, 'room_type'):
        booking.room_type = 'standard'
    if not hasattr(booking, 'room_upgrade_cost'):
        booking.room_upgrade_cost = 0
    if not hasattr(booking, 'taxes'):
        booking.taxes = decimal.Decimal(booking.total_amount * decimal.Decimal('0.12'))
    if not hasattr(booking, 'payment_method'):
        booking.payment_method = 'Credit Card'
    
    context = {
        'booking': booking,
    }
    return render(request, 'hotels/booking_confirmation.html', context)
