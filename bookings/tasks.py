from celery import shared_task
from bookings.models import Booking
from django.utils import timezone
from datetime import timedelta


@shared_task(expires=60)
def manage_expired_and_unpaid_bookings():
    """
    Проверяет все активные бронирования:
    1. Завершает бронирования, если они истекли.
    2. Отменяет бронирования, если они не были оплачены в течение 20 минут.
    """
    now = timezone.now()
    timeout = timedelta(minutes=20)

    # Завершение бронирований, у которых время окончания прошло
    expired_bookings = Booking.objects.filter(status='active', end_time__lt=now)
    for booking in expired_bookings:
        booking.status = 'completed'
        booking.parking_place.status = 'available'  # Освобождение парковочного места
        booking.parking_place.save()
        booking.save()

    # Отмена бронирований, которые не были оплачены в течение 20 минут
    unpaid_bookings = Booking.objects.filter(status='active', payment__isnull=True, start_time__lte=now - timeout)
    for booking in unpaid_bookings:
        booking.status = 'cancelled'
        booking.parking_place.status = 'available'  # Освобождение парковочного места
        booking.parking_place.save()
        booking.save()
