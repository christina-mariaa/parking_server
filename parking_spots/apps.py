from django.apps import AppConfig


class ParkingSpotsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'parking_spots'

    def ready(self):
        import parking_spots.signals
