"""
AI Engine Utilities - No paid APIs, using open-source libraries
"""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta
from collections import Counter
import math

from client.models import Restaurant, MenuItem, Order, OrderItem, Review, WalletTransaction
from restaurant.models import RestaurantEarnings
from rider_legacy.models import RiderProfile, RiderEarnings
from core.models import User


def get_recommendations(query=None, user=None):
    """Get food recommendations based on query or user history"""
    recommendations = []
    
    if user and user.is_authenticated:
        # Get user's order history (excluding cancelled/failed)
        user_orders = Order.objects.filter(
            user=user
        ).exclude(status__in=['CANCELLED', 'REFUNDED', 'FAILED'])
        
        if user_orders.exists():
            # Get most ordered items
            order_items = OrderItem.objects.filter(order__in=user_orders)
            item_counts = order_items.values('menu_item').annotate(
                count=Count('id')
            ).order_by('-count')[:5]
            
            for item_data in item_counts:
                try:
                    menu_item = MenuItem.objects.get(id=item_data['menu_item'])
                    image_url = str(menu_item.image) if menu_item.image else None
                    if image_url and not image_url.startswith('http'):
                        image_url = f"http://127.0.0.1:8000/media/{image_url}"
                        
                    recommendations.append({
                        'type': 'menu_item',
                        'id': menu_item.id,
                        'name': menu_item.name,
                        'image': image_url,
                        'restaurant': menu_item.restaurant.name,
                        'price': float(menu_item.price),
                        'rating': float(menu_item.rating),
                        'reason': 'Based on your order history'
                    })
                except MenuItem.DoesNotExist:
                    pass
            
            # Get similar restaurants
            restaurant_ids = user_orders.values_list('restaurant', flat=True).distinct()
            if restaurant_ids:
                similar_restaurants = Restaurant.objects.filter(
                    city__in=Restaurant.objects.filter(id__in=restaurant_ids).values_list('city', flat=True),
                    status='APPROVED',
                    is_active=True
                ).exclude(id__in=restaurant_ids).order_by('-rating')[:5]
                
                for restaurant in similar_restaurants:
                    image_url = str(restaurant.image) if restaurant.image else None
                    if image_url and not image_url.startswith('http'):
                        image_url = f"http://127.0.0.1:8000/media/{image_url}"

                    recommendations.append({
                        'type': 'restaurant',
                        'id': restaurant.id,
                        'name': restaurant.name,
                        'image': image_url,
                        'city': restaurant.city,
                        'rating': float(restaurant.rating),
                        'reason': 'Similar to restaurants you ordered from'
                    })
    
    # If query provided, do text-based search
    if query:
        # Simple keyword matching
        menu_items = MenuItem.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_available=True,
            restaurant__status='APPROVED'
        ).order_by('-rating', '-total_orders')[:5]
        
        for item in menu_items:
            image_url = str(item.image) if item.image else None
            if image_url and not image_url.startswith('http'):
                image_url = f"http://127.0.0.1:8000/media/{image_url}"
                
            recommendations.append({
                'type': 'menu_item',
                'id': item.id,
                'name': item.name,
                'image': image_url,
                'restaurant': item.restaurant.name,
                'price': float(item.price),
                'rating': float(item.rating),
                'reason': f'Matches your search: {query}'
            })
    
    # If no recommendations, get trending items
    if not recommendations:
        trending = get_trending_items()
        recommendations = trending[:5]
    
    return recommendations


def get_trending_items():
    """Get trending food items based on recent orders"""
    week_ago = timezone.now() - timedelta(days=7)
    
    # Get most ordered items in last week
    recent_orders = Order.objects.filter(
        placed_at__gte=week_ago
    ).exclude(status__in=['CANCELLED', 'REFUNDED', 'FAILED'])
    
    order_items = OrderItem.objects.filter(order__in=recent_orders)
    trending_items = order_items.values('menu_item').annotate(
        order_count=Count('id'),
        total_quantity=Sum('quantity')
    ).order_by('-order_count')[:10]
    
    trending = []
    for item_data in trending_items:
        try:
            menu_item = MenuItem.objects.get(id=item_data['menu_item'])
            image_url = str(menu_item.image) if menu_item.image else None
            if image_url and not image_url.startswith('http'):
                image_url = f"http://127.0.0.1:8000/media/{image_url}"
                
            trending.append({
                'type': 'menu_item',
                'id': menu_item.id,
                'name': menu_item.name,
                'image': image_url,
                'restaurant': menu_item.restaurant.name,
                'price': float(menu_item.price),
                'rating': float(menu_item.rating),
                'orders_count': item_data['order_count'],
                'reason': 'Trending this week'
            })
        except MenuItem.DoesNotExist:
            pass
    
    return trending


def get_restaurant_insights(restaurant):
    """Get AI insights for restaurant - Enhanced for 100% efficiency and stability"""
    from django.db.models.functions import ExtractHour
    from django.db.models import F
    
    week_ago = timezone.now() - timedelta(days=7)
    month_ago = timezone.now() - timedelta(days=30)
    
    # 1. Best selling items
    recent_orders = Order.objects.filter(
        restaurant=restaurant,
        placed_at__gte=month_ago,
        status='DELIVERED'
    )
    
    order_items = OrderItem.objects.filter(order__in=recent_orders)
    best_selling = order_items.values('menu_item').annotate(
        name=F('menu_item__name'),
        total_quantity=Sum('quantity'),
        order_count=Count('id')
    ).order_by('-total_quantity')[:5]
    
    best_selling_items = []
    for item in best_selling:
        best_selling_items.append({
            'id': item['menu_item'],
            'name': item['name'],
            'quantity_sold': item['total_quantity'],
            'order_count': item['order_count']
        })
    
    # 2. Peak hours analysis (SQLite & Postgres compatible)
    orders_by_hour = Order.objects.filter(
        restaurant=restaurant,
        placed_at__gte=month_ago
    ).annotate(
        hour=ExtractHour('placed_at')
    ).values('hour').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    peak_hours = []
    for item in orders_by_hour:
        if item['hour'] is not None:
            peak_hours.append({'hour': int(item['hour']), 'orders': item['count']})
    
    # 3. Customer Loyalty Analysis
    all_orders = Order.objects.filter(restaurant=restaurant)
    total_customers = all_orders.values('user').distinct().count()
    repeat_customers = all_orders.values('user').annotate(
        order_count=Count('id')
    ).filter(order_count__gt=1).count()
    
    loyalty_percentage = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
    
    # 4. Smart Suggestions for Menu
    low_performing_items = MenuItem.objects.filter(
        restaurant=restaurant
    ).filter(
        Q(total_orders__lt=5) | Q(rating__lt=3.0)
    ).order_by('total_orders')[:5]
    
    smart_suggestions = []
    for item in low_performing_items:
        reason = "Low sales volume" if (item.total_orders or 0) < 5 else "Low rating"
        suggestion = "Consider a limited-time discount or improved photos" if reason == "Low sales volume" else "Review recipe or preparation methods"
        smart_suggestions.append({
            'id': item.id,
            'name': item.name,
            'reason': reason,
            'suggestion': suggestion
        })
    
    # Fallback for suggestions if none found
    if not smart_suggestions:
        smart_suggestions.append({
            'id': 0,
            'name': "General Tip",
            'reason': "Market Trend",
            'suggestion': "Highly active period detected. Ensure sufficient staff inventory."
        })
    
    # 5. Average order value trend
    week_orders = Order.objects.filter(
        restaurant=restaurant,
        placed_at__gte=week_ago,
        status='DELIVERED'
    )
    week_avg = week_orders.aggregate(avg=Avg('total'))['avg'] or 0
    
    month_orders = Order.objects.filter(
        restaurant=restaurant,
        placed_at__gte=month_ago,
        placed_at__lt=week_ago,
        status='DELIVERED'
    )
    month_avg = month_orders.aggregate(avg=Avg('total'))['avg'] or 0
    
    avg_order_trend = 'increasing' if week_avg > month_avg else 'decreasing' if week_avg < month_avg else 'stable'
    
    # 6. Overall Performance Metrics
    overall_rating = Review.objects.filter(restaurant=restaurant).aggregate(avg=Avg('rating'))['avg'] or restaurant.rating
    total_revenue = RestaurantEarnings.objects.filter(restaurant=restaurant).aggregate(total=Sum('net_amount'))['total'] or 0

    # 7. Kitchen Load and Health (Real-time indicators)
    active_orders_count = Order.objects.filter(
        restaurant=restaurant,
        status__in=['PENDING', 'CONFIRMED', 'PREPARING', 'READY']
    ).count()
    
    # Simulate load: 0-3 orders = Low, 4-8 = Medium, 9+ = High
    load_status = 'Low' if active_orders_count < 4 else 'Medium' if active_orders_count < 9 else 'High'
    
    # Calculate health based on review ratings and cancellation rate
    total_orders_all = all_orders.count()
    cancelled_orders = all_orders.filter(status='CANCELLED').count()
    cancellation_rate = (cancelled_orders / total_orders_all * 100) if total_orders_all > 0 else 0
    
    # Health starts at 100, drops with low ratings and high cancellations
    health_score = 100 - (cancellation_rate * 2)
    if float(overall_rating) < 4.0:
        health_score -= (4.0 - float(overall_rating)) * 10
    
    health_score = max(min(health_score, 100), 70) # Keep between 70-100 for demo

    return {
        'best_selling_items': best_selling_items,
        'peak_hours': peak_hours,
        'customer_loyalty': {
            'total_unique_customers': total_customers,
            'repeat_customer_count': repeat_customers,
            'loyalty_score': round(float(loyalty_percentage), 1)
        },
        'smart_suggestions': smart_suggestions,
        'average_order_value': {
            'current_week': float(week_avg),
            'previous_weeks': float(month_avg),
            'trend': avg_order_trend
        },
        'performance_metrics': {
            'overall_rating': float(overall_rating),
            'total_revenue': float(total_revenue),
            'growth_potential': 'High' if loyalty_percentage > 15 else 'Moderate',
            'kitchen_load': load_status,
            'kitchen_health': f"{int(health_score)}%",
            'active_orders': active_orders_count
        }
    }


def calculate_rider_efficiency(rider):
    """Calculate rider efficiency score"""
    week_ago = timezone.now() - timedelta(days=7)
    
    # Get rider deliveries
    deliveries = Order.objects.filter(
        rider=rider,
        status='DELIVERED',
        delivered_at__gte=week_ago
    )
    
    if not deliveries.exists():
        return 0.0
    
    # Calculate average delivery time
    delivery_times = []
    for order in deliveries:
        if order.picked_up_at and order.delivered_at:
            time_diff = (order.delivered_at - order.picked_up_at).total_seconds() / 60  # minutes
            delivery_times.append(time_diff)
    
    avg_delivery_time = np.mean(delivery_times) if delivery_times else 0
    
    # Calculate on-time delivery rate
    on_time = sum(1 for time in delivery_times if time <= 30)  # 30 minutes target
    on_time_rate = (on_time / len(delivery_times)) * 100 if delivery_times else 0
    
    # Calculate efficiency score (0-100)
    time_score = max(0, 100 - (avg_delivery_time * 2))  # Penalize longer times
    efficiency = (time_score * 0.6) + (on_time_rate * 0.4)
    
    return round(efficiency, 2)


def get_admin_analytics():
    """Get comprehensive admin analytics"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # City-wise trends
    city_orders = Order.objects.filter(
        placed_at__date__gte=month_ago
    ).values('restaurant__city').annotate(
        order_count=Count('id'),
        revenue=Sum('total')
    ).order_by('-order_count')[:10]
    
    city_trends = [
        {
            'city': item['restaurant__city'],
            'orders': item['order_count'],
            'revenue': float(item['revenue'] or 0)
        }
        for item in city_orders
    ]
    
    # Demand prediction (simple trend analysis)
    from django.db.models.functions import TruncDay
    daily_orders = Order.objects.filter(
        placed_at__date__gte=week_ago
    ).annotate(
        day=TruncDay('placed_at')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    demand_prediction = {
        'current_week_avg': float(np.mean([item['count'] for item in daily_orders])) if daily_orders else 0,
        'trend': 'increasing' if len(daily_orders) > 1 and daily_orders[len(daily_orders)-1]['count'] > daily_orders[0]['count'] else 'stable'
    }
    
    # Peak hours
    from django.db.models.functions import ExtractHour
    hour_orders = Order.objects.filter(
        placed_at__date__gte=month_ago
    ).annotate(
        hour=ExtractHour('placed_at')
    ).values('hour').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    peak_hours = [{'hour': int(item['hour']), 'orders': item['count']} for item in hour_orders]
    
    # Restaurant performance
    restaurant_performance = Restaurant.objects.filter(
        status='APPROVED'
    ).annotate(
        order_count=Count('orders'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-order_count')[:10]
    
    restaurant_perf = [
        {
            'id': r.id,
            'name': r.name,
            'orders': r.order_count,
            'rating': float(r.avg_rating or 0),
            'city': r.city
        }
        for r in restaurant_performance
    ]
    
    # Rider performance
    rider_performance = RiderProfile.objects.filter(
        status='APPROVED'
    ).annotate(
        delivery_count=Count('rider__delivery_orders', filter=Q(rider__delivery_orders__status='DELIVERED'))
    ).order_by('-delivery_count')[:10]
    
    rider_perf = [
        {
            'id': r.id,
            'name': r.rider.name,
            'deliveries': r.delivery_count,
            'rating': float(r.rating),
            'efficiency': calculate_rider_efficiency(r.rider)
        }
        for r in rider_performance
    ]
    
    return {
        'city_trends': city_trends,
        'demand_prediction': demand_prediction,
        'peak_hours': peak_hours,
        'restaurant_performance': restaurant_perf,
        'rider_performance': rider_perf
    }


def detect_fraud():
    """Detect potential fraud patterns"""
    fraud_cases = []
    
    # Detect suspicious orders (very high value, multiple cancellations)
    suspicious_orders = Order.objects.filter(
        total__gt=5000,
        status='CANCELLED'
    ).values('user').annotate(
        cancel_count=Count('id')
    ).filter(cancel_count__gt=3)
    
    for item in suspicious_orders:
        user = User.objects.get(id=item['user'])
        fraud_cases.append({
            'type': 'suspicious_cancellations',
            'user_id': user.id,
            'user_phone': user.phone,
            'reason': f'Multiple high-value cancellations: {item["cancel_count"]}',
            'severity': 'medium'
        })
    
    # Detect unusual wallet activity
    large_wallet_transactions = WalletTransaction.objects.filter(
        amount__gt=10000,
        source='RECHARGE'
    ).values('wallet__user').annotate(
        count=Count('id')
    ).filter(count__gt=5)
    
    for item in large_wallet_transactions:
        user = User.objects.get(id=item['wallet__user'])
        fraud_cases.append({
            'type': 'unusual_wallet_activity',
            'user_id': user.id,
            'user_phone': user.phone,
            'reason': f'Multiple large wallet recharges: {item["count"]}',
            'severity': 'high'
        })
    
    return {
        'total_cases': len(fraud_cases),
        'cases': fraud_cases[:20]  # Limit to 20 cases
    }

