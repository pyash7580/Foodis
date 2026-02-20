from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'restaurants', views.RestaurantViewSet, basename='restaurant')
router.register(r'menu-items', views.MenuItemViewSet, basename='menu-item')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'coupons', views.CouponViewSet, basename='coupon')
router.register(r'wallet', views.WalletViewSet, basename='wallet')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'rider-reviews', views.RiderReviewViewSet, basename='rider-review')
router.register(r'profile', views.ProfileViewSet, basename='profile')
router.register(r'addresses', views.AddressViewSet, basename='address')
router.register(r'saved-payments', views.SavedPaymentMethodViewSet, basename='saved-payment')
router.register(r'favourite-restaurants', views.FavouriteRestaurantViewSet, basename='favourite-restaurant')
router.register(r'favourite-menu-items', views.FavouriteMenuItemViewSet, basename='favourite-menu-item')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', views.search_restaurants, name='search'),
    path('recommendations/', views.get_recommendations_view, name='recommendations'),
    path('trending/', views.get_trending_view, name='trending'),
]

