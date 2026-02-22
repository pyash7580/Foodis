"""
URL configuration for foodis project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth endpoints (login, OTP, profile)
    path('api/auth/', include('core.urls')),
    
    # Client endpoints (restaurants, orders)
    path('api/client/', include('client.urls')),
    
    # Restaurant management endpoints
    path('api/restaurant/', include('restaurant.urls')),
    
    # Rider endpoints
    path('api/rider/', include('rider.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
