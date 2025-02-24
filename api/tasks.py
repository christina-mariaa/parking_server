from celery import shared_task
from api.models import Booking
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.utils.timezone import now

@shared_task
def manage_expired_and_unpaid_bookings():
    """
    Проверяет все активные бронирования:
    1. Завершает бронирования, если они истекли.
    2. Отменяет бронирования, если они не были оплачены в течение 20 минут.
    """
    now = timezone.now()
    timeout = timedelta(minutes=20)

    # Завершаем бронирования, у которых время окончания прошло
    expired_bookings = Booking.objects.filter(status='active', end_time__lt=now)
    for booking in expired_bookings:
        booking.status = 'completed'
        booking.parking_place.status = 'available'  # Освобождаем парковочное место
        booking.parking_place.save()
        booking.save()  # Сохраняем изменения

    # Отменяем бронирования, которые не были оплачены в течение 20 минут
    unpaid_bookings = Booking.objects.filter(status='active', payment__isnull=True, start_time__lte=now - timeout)
    for booking in unpaid_bookings:
        booking.status = 'cancelled'
        booking.parking_place.status = 'available'  # Освобождаем парковочное место
        booking.parking_place.save()
        booking.save()  # Сохраняем изменения
