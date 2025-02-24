import json
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import datetime


class ParkingMapConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Подключение клиента к группе обновлений парковки
        await self.channel_layer.group_add("parking_updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Отключение клиента от группы
        await self.channel_layer.group_discard("parking_updates", self.channel_name)

    async def send_parking_update(self, event):
        # Отправление обновления о парковочном месте клиенту
        await self.send(text_data=json.dumps(event["data"]))


def notify_users_about_user_change(user, action):
    """
    Отправляет уведомление через WebSocket о создании или обновлении пользователя.
    """
    channel_layer = get_channel_layer()
    message = {
        'type': 'user.change',
        'action': action,
        'data': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'date_joined': user.date_joined.isoformat(),
            'is_staff': user.is_staff,
        }
    }
    # Отправляем сообщение в группу admin_users
    async_to_sync(channel_layer.group_send)(
        "admin_users",
        {
            "type": "send_message",
            "message": json.dumps(message),
        }
    )


class AdminUserConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = "admin_users"
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def send_message(self, event):
        message = event['message']
        self.send(text_data=message)


def notify_users_about_car_change(car, action):
    """
    Отправляет уведомление через WebSocket о создании или обновлении автомобиля.
    """
    channel_layer = get_channel_layer()
    message = {
        'type': 'car.change',
        'action': action,
        'data': {
            'id': car.id,
            'license_plate': car.license_plate,
            'user_email': car.user.email,
            'make': car.make,
            'model': car.model,
            'color': car.color,
            'registered_at': car.registered_at.isoformat(),
            'is_deleted': car.is_deleted,
        }
    }
    # Отправляем сообщение в группу admin_cars
    async_to_sync(channel_layer.group_send)(
        "admin_cars",
        {
            "type": "send_message",
            "message": json.dumps(message),
        }
    )


class AdminCarConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = "admin_cars"
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def send_message(self, event):
        message = event['message']
        self.send(text_data=message)


def notify_users_about_booking_change(booking, action):
    """
    Отправляет уведомление через WebSocket о создании или обновлении бронирования.
    """
    channel_layer = get_channel_layer()
    message = {
        'type': 'booking.change',
        'action': action,
        'data': {
            "id": booking.id,
            "status": booking.status,
            "car_license_plate": booking.car.license_plate,
            "user_email": booking.car.user.email,
            "parking_place": booking.parking_place.spot_number,
            "start_time": booking.start_time.isoformat(),
            "end_time": booking.end_time.isoformat(),
            "tariff_name": booking.tariff.name
        }
    }
    # Отправляем сообщение в группу admin_bookings
    async_to_sync(channel_layer.group_send)(
        "admin_bookings",
        {
            "type": "send_message",
            "message": json.dumps(message),
        }
    )


class AdminBookingConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = "admin_bookings"
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def send_message(self, event):
        message = event['message']
        self.send(text_data=message)


def notify_users_about_payment_change(payment, action):
    """
    Отправляет уведомление через WebSocket о создании оплаты.
    """
    channel_layer = get_channel_layer()
    message = {
        'type': 'payment.change',
        'action': action,
        'data': {
            "id": payment.id,
            "amount": float(payment.amount),
            "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
            "booking_id": payment.booking.id,
            "user_email": payment.booking.car.user.email,
            "tariff_name": payment.booking.tariff.name,
        }
    }
    async_to_sync(channel_layer.group_send)(
        "admin_payments",
        {
            "type": "send_message",
            "message": json.dumps(message),
        }
    )


class AdminPaymentConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = "admin_payments"
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def send_message(self, event):
        message = event['message']
        self.send(text_data=message)