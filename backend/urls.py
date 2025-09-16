from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

# Simple view to handle unwanted API requests
def api_models_view(request):
    return HttpResponse('', status=204)  # No Content

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('hotels.urls')),
    path('v1/models', api_models_view, name='api_models'),  # Handle unwanted requests
    path('v1/models/', api_models_view, name='api_models_slash'),  # Handle unwanted requests with slash
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else '')