import os
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import MenuItem
from client.serializers import MenuItemSerializer
from rest_framework.request import Request
from django.test import RequestFactory

try:
    req = Request(RequestFactory().get('/'))
    dish = MenuItem.objects.filter(image='').first()
    print("Dish ID:", dish.id if dish else "None")
    serializer = MenuItemSerializer(dish, context={'request': req})
    print(serializer.data)
except Exception:
    print(traceback.format_exc())
