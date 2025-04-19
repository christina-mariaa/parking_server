from django.dispatch import receiver
from django.db.models.signals import post_save
from realtime.notifications.payments import notify_users_about_payment_change
from .models import Payment


@receiver(post_save, sender=Payment)
def payment_change_handler(instance, created, **kwargs):
    if created:
        action = 'created'
    else:
        action = 'updated'
    notify_users_about_payment_change(instance, action)
