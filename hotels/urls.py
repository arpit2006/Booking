from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'hotels', views.HotelViewSet)
router.register(r'bookings', views.BookingViewSet, basename='booking')
router.register(r'cities', views.CityViewSet)
router.register(r'amenities', views.AmenityViewSet)

app_name = 'hotels'

urlpatterns = [
    # Web views
    path('', views.home_view, name='home'),
    path('hotels/', views.hotel_list_view, name='hotel_list'),
    path('hotels/<slug:slug>/', views.hotel_detail_view, name='hotel_detail'),
    path('book/<slug:slug>/', views.book_hotel_view, name='book_hotel'),
    path('booking/<str:booking_id>/confirmation/', views.booking_confirmation_view, name='booking_confirmation'),
    
    # API endpoints
    path('api/', include(router.urls)),
]