from asgiref.sync import async_to_sync
from django.dispatch import receiver
from django.db.models.signals import post_save
from realtime.notifications.access_logs import notify_users_about_logs_change
from .models import QRAccessLog


@receiver(post_save, sender=QRAccessLog)
def access_log_add_handler(instance, created, **kwargs):
    booking = instance.booking
    if booking:
        _ = booking.id
    async_to_sync(notify_users_about_logs_change)(instance)
