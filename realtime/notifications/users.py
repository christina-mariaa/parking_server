import json
from channels.layers import get_channel_layer


async def notify_users_about_user_change(user, action):
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
    await channel_layer.group_send(
        "admin_users",
        {
            "type": "send_message",
            "message": json.dumps(message),
        }
    )
