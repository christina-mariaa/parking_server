import json
from channels.layers import get_channel_layer


async def notify_users_about_payment_change(payment):
    """
    Отправляет уведомление через WebSocket о создании оплаты.
    """
    channel_layer = get_channel_layer()
    message = {
        'type': 'payment.change',
        'data': {
            "id": payment.id,
            "amount": float(payment.amount),
            "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
            "booking_id": payment.booking.id,
            "user_email": payment.booking.car.user.email,
            "tariff_name": payment.booking.tariff.name,
        }
    }
    await channel_layer.group_send(
        "admin_payments",
        {
            "type": "send_message",
            "message": json.dumps(message),
        }
    )
    