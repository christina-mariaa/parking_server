from django.dispatch import receiver
from django.db.models.signals import post_save
from realtime.notifications.users import notify_users_about_user_change
from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def user_change_handler(instance, created, **kwargs):
    if created:
        action = 'created'
    else:
        action = 'updated'
    notify_users_about_user_change(instance, action)
