import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import Order
from django.db.models import Q

def debug():
    city_filters = Q(city_id=1) | Q(restaurant__city_id=1) | Q(restaurant__city__iexact='Mehsana')
    
    orders = Order.objects.filter(city_filters, status__in=['CONFIRMED', 'PREPARING', 'READY'], rider__isnull=True).select_related('restaurant')
    
    for o in orders:
        print(f"Order: {o.id} | Order City ID: {o.city_id_id} | Rest City ID: {o.restaurant.city_id_id} | Rest City Name: {o.restaurant.city}")
        
if __name__ == '__main__':
    debug()
