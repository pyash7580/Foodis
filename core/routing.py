from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notifications/(?P<user_id>\w+)/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/order/(?P<order_id>\w+)/$', consumers.OrderTrackingConsumer.as_asgi()),
    # Backward-compatible alias (older frontend uses /ws/orders/<order_id>/)
    re_path(r'ws/orders/(?P<order_id>\w+)/$', consumers.OrderTrackingConsumer.as_asgi()),
]

