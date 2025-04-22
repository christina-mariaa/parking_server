from django.dispatch import receiver
from django.db.models.signals import post_save
from realtime.notifications.parking_spots import notify_users_about_parking_spots_change
from .models import ParkingSpot
from asgiref.sync import async_to_sync


@receiver(post_save, sender=ParkingSpot)
def notify_parking_spot_update(instance, **kwargs):
    async_to_sync(notify_users_about_parking_spots_change)(instance)
