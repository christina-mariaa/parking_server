from channels.generic.websocket import AsyncWebsocketConsumer


class AdminBookingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("admin_bookings", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("admin_bookings", self.channel_name)

    async def send_message(self, event):
        message = event['message']
        await self.send(text_data=message)
        