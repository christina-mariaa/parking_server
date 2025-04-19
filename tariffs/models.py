from django.db import models
from datetime import timedelta


class Tariff(models.Model):
    """
    Модель, представляющая тариф для бронирования парковочного места.

    Поля:
    - name (CharField): Тип тарифа ('daily' или 'monthly').
    - price (DecimalField): Стоимость тарифа.
    - created_at (DateTimeField): Дата создания тарифа (устанавливается автоматически).
    - updated_at (DateTimeField): Дата последнего обновления тарифа (устанавливается автоматически).

    Методы:
    - get_duration_delta(): Возвращает длительность действия тарифа как timedelta.
      * 'daily' → 1 день
      * 'monthly' → 30 дней
    """
    DURATION_CHOICES = [
        ('daily', 'Дневной'),  # 1 день
        ('monthly', 'Месячный')  # 30 дней
    ]
    name = models.CharField(max_length=50, choices=DURATION_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_duration_delta(self):
        """
        Возвращает длительность действия тарифа в днях.
        """
        if self.name == 'daily':
            return timedelta(days=1)
        elif self.name == 'monthly':
            return timedelta(days=30)
        return timedelta()
