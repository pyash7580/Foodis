from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profile', views.RiderProfileViewSet, basename='rider-profile')
router.register(r'orders', views.OrderViewSet, basename='rider-order')
router.register(r'earnings', views.RiderEarningsViewSet, basename='rider-earnings')
router.register(r'reviews', views.RiderReviewViewSet, basename='rider-review')
router.register(r'onboarding', views.RiderOnboardingViewSet, basename='rider-onboarding')
router.register(r'notifications', views.RiderNotificationViewSet, basename='rider-notification')
router.register(r'incentives', views.IncentiveViewSet, basename='rider-incentive')

urlpatterns = [
    path('login-status/', views.rider_login_status, name='rider-login-status'),
    path('', include(router.urls)),
]

