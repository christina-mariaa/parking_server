from channels.layers import get_channel_layer
import json


async def notify_users_about_parking_spots_change(spot):
    """
    Отправляет уведомление через WebSocket об изменении статуса места.
    """
    channel_layer = get_channel_layer()
    message = {
        "spot_number": spot.spot_number,
        "status": spot.status
    }
    await channel_layer.group_send(
        "parking_updates",
        {
            "type": "send_parking_update",
            "message": json.dumps(message)
        }
    )

