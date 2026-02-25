"""
URL configuration for foodis project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.shortcuts import render
from core import views as core_views
from .dashboard import dashboard_view


# ✅ Homepage view
def home(request):
    return render(request, "index.html")

# ✅ Healthcheck endpoint (Railway compatible)
def health_check(request):
    return HttpResponse("OK_V2.3", status=200)


urlpatterns = [
    # ✅ Dashboard Path
    path("dashboard/", dashboard_view),

    # ✅ Railway Healthcheck
    path("health/", health_check),
    path("test-deploy/", lambda r: HttpResponse("DEPLOY_V2.3_SUCCESS")),
    path("api/health/", core_views.health_check_view),

    # Admin
    path("admin/", admin.site.urls),

    # Auth endpoints (login, OTP, profile)
    path("api/auth/", include("core.urls")),

    # Client endpoints (restaurants, orders)
    path("api/client/", include("client.urls")),

    # Restaurant management endpoints
    path("api/restaurant/", include("restaurant.urls")),

    # Rider endpoints
    path("api/rider/", include("rider.urls")),

    # Admin panel endpoints
    path("api/admin/", include("admin_panel.urls")),
]


# ✅ Serve media files in development only
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
