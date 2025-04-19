from django.db import models


class ParkingSpot(models.Model):
    """
    Модель, представляющая парковочное место.

    Атрибуты:
        spot_number (int): Уникальный номер парковочного места (используется как первичный ключ);
        status (str): Текущий статус парковочного места. Может быть:
            - 'booked' — место забронировано,
            - 'available' — место доступно для бронирования,
            - 'unavailable' — место временно недоступно для бронирования.
    """
    STATUSES = [
        ('booked', 'забронировано'),
        ('available', 'свободно'),
        ('unavailable', 'недоступно для бронирования')
    ]
    spot_number = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=50, choices=STATUSES)
