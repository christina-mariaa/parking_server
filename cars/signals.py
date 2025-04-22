from asgiref.sync import async_to_sync
from django.dispatch import receiver
from django.db.models.signals import post_save
from realtime.notifications.cars import notify_users_about_car_change
from .models import Car


@receiver(post_save, sender=Car)
def car_change_handler(instance, created, **kwargs):
    if created:
        action = 'created'
    else:
        action = 'updated'
    async_to_sync(notify_users_about_car_change)(instance, action)
