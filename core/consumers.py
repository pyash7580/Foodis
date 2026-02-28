import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications"""
    
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'notifications_{self.user_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # If user is a rider, also join their city-specific assignment channel
        rider = await self.get_rider_details(self.user_id)
        if rider and rider.get('city'):
            self.rider_city_group = f"rider_assignments_{rider['city']}"
            await self.channel_layer.group_add(
                self.rider_city_group,
                self.channel_name
            )
        
        await self.accept()

    @database_sync_to_async
    def get_rider_details(self, user_id):
        from rider.models import Rider
        from core.city_utils import normalize_city_name
        try:
            # Look up rider by user ForeignKey instead of phone
            rider = Rider.objects.get(user_id=user_id)
            normalized_city = normalize_city_name(rider.city)
            return {'city': normalized_city}
        except Rider.DoesNotExist:
            return None
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Leave rider city group if applicable
        if hasattr(self, 'rider_city_group'):
            await self.channel_layer.group_discard(
                self.rider_city_group,
                self.channel_name
            )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'notification_message',
                'message': message
            }
        )
    
    # Receive message from room group
    async def notification_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


class OrderTrackingConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time order tracking"""
    
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'order_{self.order_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Optionally send current state immediately (could be done via initial API fetch too)
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket (primarily from Riders)
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'location_update':
            location = data.get('location')
            
            # Enforcement: Check if user is a rider and override with city-locked location
            user = self.scope.get('user')
            if user and user.is_authenticated and user.role == 'RIDER':
                locked_location = await self.get_rider_locked_location(user.id)
                if locked_location:
                    location = locked_location

            # Broadcast location update
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'order_location_message',
                    'location': location
                }
            )
        elif message_type == 'status_update':
            status = data.get('status')
            # Broadcast status update
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'order_status_message',
                    'status': status
                }
            )

    @database_sync_to_async
    def get_rider_locked_location(self, user_id):
        from rider.models import Rider
        try:
            rider = Rider.objects.get(user_id=user_id)
            if rider.is_online and rider.city in rider.CITY_CENTERS:
                center = rider.CITY_CENTERS[rider.city]
                return {'latitude': center['lat'], 'longitude': center['lng']}
        except Rider.DoesNotExist:
            pass
        return None
    
    # Handlers for messages sent to the group
    async def order_status_message(self, event):
        """Broadcast status update to client"""
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': event['status'],
            'timestamp': event.get('timestamp')
        }))

    async def order_location_message(self, event):
        """Broadcast location update to client"""
        await self.send(text_data=json.dumps({
            'type': 'location_update',
            'location': event['location']
        }))

