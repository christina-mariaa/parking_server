from celery import shared_task
from api.models import Booking


@shared_task
def release_booking_if_not_paid(booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, status='active')
        # Проверяем, есть ли оплата
        if not hasattr(booking, 'payment'):
            # Если оплаты нет, отменяем бронирование
            booking.status = 'cancelled'
            booking.save()

            # Обновляем статус парковочного места
            booking.parking_place.status = 'available'
            booking.parking_place.save()
    except Booking.DoesNotExist:
        pass  # Бронирование уже обработано
