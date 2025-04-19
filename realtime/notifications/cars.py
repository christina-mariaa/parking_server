import json
from channels.layers import get_channel_layer


async def notify_users_about_car_change(car, action):
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
    await channel_layer.group_send(
        "admin_cars",
        {
            "type": "send_message",
            "message": json.dumps(message),
        }
    )
