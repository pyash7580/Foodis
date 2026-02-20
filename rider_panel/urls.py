from django.urls import path
from .views import auth_views, dashboard_views

app_name = 'rider_panel'

urlpatterns = [
    # Auth
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('verify/', auth_views.VerifyOTPView.as_view(), name='verify_otp'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('dashboard/', dashboard_views.DashboardView.as_view(), name='dashboard'),
]
