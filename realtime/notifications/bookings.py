import json
from channels.layers import get_channel_layer


async def notify_users_about_booking_change(booking, action):
    """
    Отправляет уведомление через WebSocket о создании или обновлении бронирования.
    """
    channel_layer = get_channel_layer()

    data = {
        "id": booking.id,
        "status": booking.status,
        "car_license_plate": booking.car.license_plate,
        "user_email": booking.car.user.email,
        "parking_place": booking.parking_place.spot_number,
        "start_time": booking.start_time.isoformat(),
        "end_time": booking.end_time.isoformat(),
        "tariff_name": booking.tariff.name,
    }

    if hasattr(booking, 'payment'):
        data["payment_amount"] = float(booking.payment.amount)
        data["payment_date"] = booking.payment.payment_date.isoformat()

    message = {
        'type': 'booking.change',
        'action': action,
        'data': data
    }
    await channel_layer.group_send(
        "admin_bookings",
        {
            "type": "send_message",
            "message": json.dumps(message),
        }
    )
