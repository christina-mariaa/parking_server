from celery import shared_task
from api.models import Booking
from django.utils import timezone

@shared_task
def release_booking_if_not_paid(booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, status='active')

        if not hasattr(booking, 'payment'):
            booking.status = 'cancelled'
            booking.save()
            booking.parking_place.status = 'available'
            booking.parking_place.save()
    except Booking.DoesNotExist:
        pass


@shared_task
def complete_booking(booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        if booking.end_time <= timezone.now():
            booking.status = 'completed'
            booking.save()
            booking.parking_place.status = 'available'
            booking.parking_place.save()
    except Booking.DoesNotExist:
        pass
