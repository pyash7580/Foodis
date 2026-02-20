from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'restaurant', views.RestaurantViewSet, basename='restaurant')
router.register(r'menu-items', views.MenuItemViewSet, basename='menu-item')
router.register(r'customizations', views.MenuItemCustomizationViewSet, basename='customization')
router.register(r'customization-options', views.CustomizationOptionViewSet, basename='customization-option')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'earnings', views.RestaurantEarningsViewSet, basename='earnings')
router.register(r'coupons', views.CouponViewSet, basename='coupon')

urlpatterns = [
    path('', include(router.urls)),
]

