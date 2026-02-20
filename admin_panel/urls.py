from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'restaurants', views.RestaurantViewSet, basename='restaurant')
router.register(r'riders', views.RiderProfileViewSet, basename='rider')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'banners', views.BannerViewSet, basename='banner')
router.register(r'commissions', views.CommissionViewSet, basename='commission')
router.register(r'coupons', views.CouponViewSet, basename='coupon')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'wallet-transactions', views.WalletTransactionViewSet, basename='wallet-transaction')
router.register(r'earnings', views.RestaurantEarningsViewSet, basename='earnings')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'policies', views.SitePolicyViewSet, basename='policy')
router.register(r'menu-items', views.MenuItemViewSet, basename='menu-item')

router.register(r'settings', views.SystemSettingsViewSet, basename='setting')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
    path('dashboard/revenue-graph/', views.revenue_graph, name='revenue-graph'),
    path('analytics/', views.analytics, name='analytics'),
    path('fraud-detection/', views.fraud_detection, name='fraud-detection'),
    path('wallet/adjust/', views.adjust_wallet, name='adjust-wallet'),
]

