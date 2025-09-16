from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import User, UserProfile
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer,
    UserSerializer, UserUpdateSerializer, ChangePasswordSerializer
)


# API Views
class RegisterAPIView(generics.CreateAPIView):
    """API endpoint for user registration"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class LoginAPIView(generics.GenericAPIView):
    """API endpoint for user login"""
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Login successful'
        })


class LogoutAPIView(generics.GenericAPIView):
    """API endpoint for user logout"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
        except:
            pass
        return Response({'message': 'Logout successful'})


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """API endpoint for user profile management"""
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ChangePasswordAPIView(generics.GenericAPIView):
    """API endpoint for changing password"""
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password changed successfully'})


# Web Views
class CustomLoginView(LoginView):
    """Custom login view"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return self.get_redirect_url() or '/'


class CustomLogoutView(LogoutView):
    """Custom logout view"""
    next_page = '/'


class RegisterView(CreateView):
    """User registration view"""
    model = User
    template_name = 'accounts/register.html'
    fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone_number', 'user_type']
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        UserProfile.objects.create(user=user)
        messages.success(self.request, 'Registration successful! Please log in.')
        return super().form_valid(form)


@login_required
def profile_view(request):
    """User profile view"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'accounts/profile.html', context)


class ProfileUpdateView(UpdateView):
    """User profile update view"""
    model = User
    template_name = 'accounts/profile_edit.html'
    fields = [
        'first_name', 'last_name', 'email', 'phone_number',
        'date_of_birth', 'profile_picture', 'address_line_1',
        'address_line_2', 'city', 'state', 'postal_code',
        'country', 'newsletter_subscription', 'preferred_currency'
    ]
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


@login_required
def dashboard_view(request):
    """User dashboard view"""
    user = request.user
    
    # Get user's bookings
    from hotels.models import Booking
    bookings = Booking.objects.filter(user=user).order_by('-created_at')[:5]
    
    context = {
        'user': user,
        'bookings': bookings,
        'total_bookings': Booking.objects.filter(user=user).count(),
    }
    
    if user.user_type == 'hotel_owner':
        # Hotel owner dashboard
        from hotels.models import Hotel
        hotels = Hotel.objects.filter(owner=user)
        hotel_bookings = Booking.objects.filter(hotel__in=hotels).order_by('-created_at')[:10]
        
        context.update({
            'hotels': hotels,
            'hotel_bookings': hotel_bookings,
            'total_hotels': hotels.count(),
            'total_revenue': sum(booking.total_price for booking in hotel_bookings),
        })
        return render(request, 'accounts/hotel_owner_dashboard.html', context)
    
    return render(request, 'accounts/dashboard.html', context)
