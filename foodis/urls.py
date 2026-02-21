"""
URL configuration for foodis project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.views import home_view, health_check_view, seed_riders_view

urlpatterns = [
    path('', home_view, name='home'),
    path('api/seed-riders/', seed_riders_view, name='seed_riders'),
    path('api/health/', health_check_view, name='health_check'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('core.urls')),
    path('api/client/', include('client.urls')),
    path('api/restaurant/', include('restaurant.urls')),
    path('api/rider/', include('rider_legacy.urls')),
    path('api/ai/', include('ai_engine.urls')),
    path('api/admin/', include('admin_panel.urls')),
    path('rider/', include('rider.urls')),
]

# Serve media files (images, uploads) in both development and production
# This is necessary for restaurant images to display on Render and other production servers
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files (CSS, JavaScript) only in development
# In production, WhiteNoise (via STATICFILES_STORAGE) and/or Render serve these
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
