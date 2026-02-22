from django.urls import path, include
from .views import LoginView, VerifyOTPView, LogoutView, DashboardView, OrderActionView, ToggleDutyView, EarningsView, RequestPayoutView, AcceptOrderView
from rider_legacy.views import rider_login_status
from .api import RiderPollingAPI
from .api_views import (
    RiderRegisterAPIView, RiderLoginAPIView, 
    RiderProfileAPIView, RiderStatusAPIView, 
    RiderLogoutAPIView
)
from .lifecycle_api import (
    AcceptOrderAPIView, PickupOrderAPIView,
    StartDeliveryAPIView, CompleteOrderAPIView,
    FailDeliveryAPIView
)

app_name = 'rider'

urlpatterns = [
    # Template Views
    path('login/', LoginView.as_view(), name='login'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('toggle-duty/', ToggleDutyView.as_view(), name='toggle_duty'),
    path('earnings/', EarningsView.as_view(), name='earnings'),
    path('request-payout/', RequestPayoutView.as_view(), name='request_payout'),
    path('order-action/<int:assignment_id>/', OrderActionView.as_view(), name='order_action'),
    path('accept-order/<int:order_id>/', AcceptOrderView.as_view(), name='accept_order'),
    path('polling-api/', RiderPollingAPI.as_view(), name='polling_api'),
    
    path('login-status/', rider_login_status, name='rider_login_status'),
    
    # API endpoints (JWT based)
    path('api/register/', RiderRegisterAPIView.as_view(), name='api_register'),
    path('api/login/', RiderLoginAPIView.as_view(), name='api_login'),
    # path('api/profile/', RiderProfileAPIView.as_view(), name='api_profile'), # Disabled: handled by rider_legacy router
    path('api/status/', RiderStatusAPIView.as_view(), name='api_status'),
    path('api/logout/', RiderLogoutAPIView.as_view(), name='api_logout'),
    
    # Order Lifecycle APIs
    path('api/orders/<int:order_id>/accept/', AcceptOrderAPIView.as_view(), name='api_order_accept'),
    path('api/orders/<int:assignment_id>/pickup/', PickupOrderAPIView.as_view(), name='api_order_pickup'),
    path('api/orders/<int:assignment_id>/start-delivery/', StartDeliveryAPIView.as_view(), name='api_order_start_delivery'),
    path('api/orders/<int:assignment_id>/complete/', CompleteOrderAPIView.as_view(), name='api_order_complete'),
    path('api/orders/<int:assignment_id>/fail/', FailDeliveryAPIView.as_view(), name='api_order_fail'),
    
    # 📌 Legacy Router Endpoints (fixes missing /api/rider/profile/ toggle_online, orders, etc)
    path('', include('rider_legacy.urls')),
]
