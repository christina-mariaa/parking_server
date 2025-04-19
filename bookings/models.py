from django.db import models
from cars.models import Car
from tariffs.models import Tariff
from parking_spots.models import ParkingSpot
from django.utils import timezone


class Booking(models.Model):
    """
    Модель бронирования парковочного места для автомобиля пользователя.

    Поля:
    - status (str): Статус бронирования. Возможные значения:
        * active — текущее активное бронирование;
        * completed — завершённое бронирование;
        * cancelled — отменённое бронирование.
    - car (ForeignKey): Автомобиль, на который оформлено бронирование.
    - parking_place (ForeignKey): Забронированное парковочное место.
    - tariff (ForeignKey): Тариф, по которому осуществляется бронирование.
    - start_time (DateTime): Время начала бронирования (устанавливается автоматически).
    - end_time (DateTime): Время окончания бронирования (рассчитывается по длительности тарифа).

    Поведение:
    - При первом сохранении (создании) объекта автоматически вычисляется `end_time`
      на основе `start_time` и длительности тарифа (`tariff.get_duration_delta()`).
    """
    STATUSES = [
        ('active', 'Активное'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено')
    ]
    status = models.CharField(max_length=20, choices=STATUSES, default='active')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='bookings')
    parking_place = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE, related_name='bookings')
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        # Проверяем, что объект ещё не сохранён
        if not self.pk:
            if not self.start_time:
                self.start_time = timezone.now()
            if self.tariff:
                self.end_time = self.start_time + self.tariff.get_duration_delta()
        super().save(*args, **kwargs)
