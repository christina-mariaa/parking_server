from asgiref.sync import async_to_sync
from django.dispatch import receiver
from django.db.models.signals import post_save
from realtime.notifications.bookings import notify_users_about_booking_change
from .models import Booking
from payments.models import Payment


@receiver(post_save, sender=Booking)
def booking_change_handler(instance, created, **kwargs):
    if created:
        action = 'created'
        instance.parking_place.status = 'booked'
        instance.parking_place.save()
    else:
        action = 'updated'

    try:
        instance.payment
    except Payment.DoesNotExist:
        pass

    async_to_sync(notify_users_about_booking_change)(instance, action)
