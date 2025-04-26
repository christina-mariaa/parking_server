from django.dispatch import receiver
from django.db.models.signals import post_save
from realtime.notifications.payments import notify_users_about_payment_change
from realtime.notifications.bookings import notify_users_about_booking_change
from .models import Payment
from asgiref.sync import async_to_sync


@receiver(post_save, sender=Payment)
def payment_change_handler(instance, created, **kwargs):
    booking = instance.booking

    _ = booking.car.license_plate
    _ = booking.car.user.email
    _ = booking.tariff.name
    _ = booking.parking_place.spot_number
    _ = instance.amount
    _ = instance.payment_date
    async_to_sync(notify_users_about_payment_change)(instance)
    async_to_sync(notify_users_about_booking_change)(instance.booking, 'updated')
