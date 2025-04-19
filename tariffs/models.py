from django.db import models
from datetime import timedelta
from api.models import CustomUser


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

    def save(self, *args, changed_by=None, **kwargs):
        """
        Сохраняет изменения в тарифе и автоматически фиксирует историю изменения цены.

        Аргументы:
        - changed_by (CustomUser, необязательный): Пользователь, который изменил цену тарифа.

        При изменении цены создаётся запись в модели TariffPriceHistory.
        """
        if self.pk:
            old_price = Tariff.objects.get(pk=self.pk).price  # Получение старой цены
            if old_price != self.price:  # Если цена обновляется
                TariffPriceHistory.objects.create(
                    tariff=self,
                    old_price=old_price,
                    new_price=self.price,
                    changed_by=changed_by
                )
        super().save(*args, **kwargs)


class TariffPriceHistory(models.Model):
    """
   Модель, представляющая историю изменения цены тарифа.

   Поля:
   - tariff (ForeignKey): Ссылка на тариф, для которого зафиксировано изменение.
   - old_price (DecimalField): Предыдущая цена тарифа.
   - new_price (DecimalField): Новая установленная цена тарифа.
   - changed_by (ForeignKey): Пользователь, который изменил цену (может быть пустым).
   - changed_at (DateTimeField): Дата и время изменения цены (устанавливается автоматически).
   """
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE, related_name='price_history')
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    changed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
