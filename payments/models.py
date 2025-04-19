from django.db import models
from bookings.models import Booking


class Payment(models.Model):
    """
    Модель оплаты бронирования парковочного места.

    Поля:
    - booking (OneToOneField): Связь с объектом бронирования. Каждое бронирование может иметь только одну оплату.
    - amount (Decimal): Сумма оплаты. Автоматически устанавливается на основе цены тарифа, связанного с бронированием.
    - payment_date (DateTime): Дата и время проведения оплаты (устанавливается автоматически при создании).

    Поведение:
    - При сохранении объекта автоматически устанавливает сумму оплаты (`amount`)
      на основе тарифа, связанного с бронированием (`booking.tariff.price`).
    """
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    payment_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Сумма автоматически устанавливается на основе цены тарифа
        self.amount = self.booking.tariff.price
        super().save(*args, **kwargs)
