import json
from channels.layers import get_channel_layer


async def notify_users_about_logs_change(access_log):
    """
    Отправляет уведомление через WebSocket о попытке доступа по QR.
    """
    channel_layer = get_channel_layer()
    message = {
        'data': {
            "id": access_log.id,
            "qr_data": access_log.qr_data,
            "access_granted": access_log.access_granted,
            "failure_reason": access_log.failure_reason,
            "failure_reason_display": access_log.get_failure_reason_display() if access_log.failure_reason else None,
            "time": access_log.time.isoformat(),
            "booking": access_log.booking.id if access_log.booking else None
        }
    }
    await channel_layer.group_send(
        "admin_access_logs",
        {
            "type": "send_message",
            "message": json.dumps(message, ensure_ascii=False),
        }
    )
