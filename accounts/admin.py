from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        'bio', 'website', 'favorite_destinations', 'travel_style',
        'facebook_url', 'twitter_url', 'instagram_url',
        'email_verified', 'phone_verified', 'identity_verified'
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'user_type',
        'is_staff', 'is_active', 'date_joined', 'profile_picture_preview'
    )
    list_filter = (
        'user_type', 'is_staff', 'is_superuser', 'is_active',
        'date_joined', 'newsletter_subscription', 'preferred_currency'
    )
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': (
                'phone_number', 'date_of_birth', 'profile_picture',
                'user_type', 'newsletter_subscription', 'preferred_currency'
            )
        }),
        ('Address Information', {
            'fields': (
                'address_line_1', 'address_line_2', 'city',
                'state', 'postal_code', 'country'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.profile_picture.url
            )
        return "No Image"
    profile_picture_preview.short_description = "Profile Picture"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'travel_style', 'email_verified',
        'phone_verified', 'identity_verified', 'created_at'
    )
    list_filter = (
        'travel_style', 'email_verified', 'phone_verified',
        'identity_verified', 'created_at'
    )
    search_fields = ('user__username', 'user__email', 'bio', 'favorite_destinations')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Profile Details', {
            'fields': ('bio', 'website', 'favorite_destinations', 'travel_style')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url'),
            'classes': ('collapse',)
        }),
        ('Verification Status', {
            'fields': ('email_verified', 'phone_verified', 'identity_verified')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
