from .models import SiteSettings


def site_settings(request):
    """Add site settings to template context"""
    try:
        settings = SiteSettings.get_settings()
        return {
            'site_settings': settings,
            'site_name': settings.site_name,
            'site_tagline': settings.site_tagline,
        }
    except:
        return {
            'site_settings': None,
            'site_name': 'BookingMVP',
            'site_tagline': 'Your Perfect Stay Awaits',
        }