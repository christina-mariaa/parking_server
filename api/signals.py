from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import *
from django.core.cache import cache
from parking_server.consumers import notify_users_about_user_change, notify_users_about_car_change, notify_users_about_booking_change, notify_users_about_payment_change

@receiver(post_save, sender=ParkingSpot)
def notify_parking_spot_update(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "parking_updates",
        {
            "type": "send_parking_update",
            "data": {
                "spot_number": instance.spot_number,
                "status": instance.status
            }
        }
    )


# @receiver(post_save, sender=ParkingMap)
# def update_cache_on_new_map(sender, instance, created, **kwargs):
#     if created:  # Только при добавлении новой карты
#         cache.delete('parking_spots')
#         parse_svg_and_cache(force_update=True)  # Принудительное обновление кэша
#         print("Кэш обновлен после загрузки новой карты")


@receiver(post_save, sender=CustomUser)
def user_change_handler(sender, instance, created, **kwargs):
    if created:
        action = 'created'
    else:
        action = 'updated'
    notify_users_about_user_change(instance, action)


@receiver(post_save, sender=Car)
def car_change_handler(sender, instance, created, **kwargs):
    if created:
        action = 'created'
    else:
        action = 'updated'
    notify_users_about_car_change(instance, action)


@receiver(post_save, sender=Booking)
def booking_change_handler(sender, instance, created, **kwargs):
    if created:
        action = 'created'
        instance.parking_place.status = 'booked'
        instance.parking_place.save()
    else:
        action = 'updated'
    notify_users_about_booking_change(instance, action)


@receiver(post_save, sender=Payment)
def payment_change_handler(sender, instance, created, **kwargs):
    if created:
        action = 'created'
    else:
        action = 'updated'
    notify_users_about_payment_change(instance, action)