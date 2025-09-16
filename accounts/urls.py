from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # Profile Management
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # API endpoints
    path('api/register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('api/logout/', views.LogoutAPIView.as_view(), name='api_logout'),
    path('api/profile/', views.UserProfileAPIView.as_view(), name='api_profile'),
    path('api/change-password/', views.ChangePasswordAPIView.as_view(), name='api_change_password'),
]
