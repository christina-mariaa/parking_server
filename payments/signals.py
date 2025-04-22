from django.dispatch import receiver
from django.db.models.signals import post_save
from realtime.notifications.payments import notify_users_about_payment_change
from .models import Payment
from asgiref.sync import async_to_sync


@receiver(post_save, sender=Payment)
def payment_change_handler(instance, created, **kwargs):
    if created:
        action = 'created'
    else:
        action = 'updated'
    _ = instance.booking.car.user.email
    _ = instance.booking.tariff.name
    async_to_sync(notify_users_about_payment_change)(instance, action)
