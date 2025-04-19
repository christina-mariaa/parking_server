from django.dispatch import receiver
from django.db.models.signals import post_save
from realtime.notifications.bookings import notify_users_about_booking_change
from .models import Booking


@receiver(post_save, sender=Booking)
def booking_change_handler(instance, created, **kwargs):
    if created:
        action = 'created'
        instance.parking_place.status = 'booked'
        instance.parking_place.save()
    else:
        action = 'updated'
    notify_users_about_booking_change(instance, action)
