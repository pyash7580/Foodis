from django.shortcuts import render, redirect
from django.db.models import Count, Sum
from client.models import Restaurant, MenuItem, Category, Order
from rider_legacy.models import RiderProfile as Rider
from core.models import User
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

def admin_required(user):
    return user.is_staff or user.role == 'ADMIN'

@user_passes_test(admin_required)
def dashboard_view(request):
    """Premium Data Explorer Dashboard with CRUD"""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        item_id = request.POST.get('id')
        model_type = request.POST.get('type')
        
        try:
            if action == 'delete':
                if model_type == 'restaurant':
                    Restaurant.objects.filter(id=item_id).delete()
                elif model_type == 'user':
                    User.objects.filter(id=item_id).delete()
                elif model_type == 'order':
                    Order.objects.filter(id=item_id).delete()
                messages.success(request, f"Deleted {model_type} #{item_id}")
                
            elif action == 'toggle_status':
                if model_type == 'restaurant':
                    rest = Restaurant.objects.get(id=item_id)
                    rest.status = 'APPROVED' if rest.status != 'APPROVED' else 'REJECTED'
                    rest.save()
                elif model_type == 'order':
                    order = Order.objects.get(id=item_id)
                    order.status = 'CANCELLED' if order.status != 'CANCELLED' else 'DELIVERED'
                    order.save()
                messages.success(request, f"Updated {model_type} #{item_id}")
            
            elif action == 'create_restaurant':
                name = request.POST.get('name')
                city = request.POST.get('city')
                cuisine = request.POST.get('cuisine')
                if name:
                    Restaurant.objects.create(name=name, city=city, cuisine=cuisine, status='APPROVED')
                    messages.success(request, f"Created restaurant: {name}")
                    
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            
        return redirect('/dashboard/')

    # Stats
    stats = {
        'restaurants': Restaurant.objects.count(),
        'riders': Rider.objects.count(),
        'users': User.objects.count(),
        'menu_items': MenuItem.objects.count(),
        'categories': Category.objects.count(),
        'orders': Order.objects.count(),
        'live_orders': Order.objects.exclude(status__in=['DELIVERED', 'CANCELLED', 'REFUNDED']).count(),
    }
    
    # Data Lists
    restaurants = Restaurant.objects.all().order_by('-created_at')[:50]
    riders = Rider.objects.all().order_by('-created_at')[:50]
    users = User.objects.all().order_by('-created_at')[:50]
    orders = Order.objects.all().order_by('-placed_at')[:50]
    
    context = {
        'stats': stats,
        'restaurants': restaurants,
        'riders': riders,
        'users': users,
        'orders': orders,
    }
    
    return render(request, "dashboard.html", context)
