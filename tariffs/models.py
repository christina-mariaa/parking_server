from django.db import models
from datetime import timedelta
from api.models import CustomUser
from django.utils.functional import cached_property


class Tariff(models.Model):
    """
    Тариф для бронирования парковочного места.

    Поля:
        name (str): Название тарифа (например, "Почасовой", "Суточный").
        price (Decimal): Стоимость тарифа.
        duration_minutes (int): Длительность действия тарифа в минутах.
        is_active (bool): Флаг, указывающий, доступен ли тариф для новых бронирований.
        created_at (datetime): Дата создания тарифа.
        updated_at (datetime): Дата последнего изменения тарифа.

    Методы:
        get_duration_delta(): Возвращает длительность тарифа как timedelta.
        duration_display: Отображает длительность в человеко-понятном виде (например, "2 часа").
        save(): При изменении цены сохраняет историю изменений (TariffPriceHistory).
    """
    name = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_duration_delta(self):
        return timedelta(minutes=self.duration_minutes)

    @cached_property
    def duration_display(self):
        minutes = self.duration_minutes
        days = minutes // 1440
        hours = (minutes % 1440) // 60
        mins = minutes % 60

        parts = []
        if days > 0:
            parts.append(f"{days} {'день' if days == 1 else 'дня' if days < 5 else 'дней'}")
        if hours > 0:
            parts.append(f"{hours} {'час' if hours == 1 else 'часа' if hours < 5 else 'часов'}")
        if mins > 0 or not parts:  # показывать минуты всегда, если всё остальное = 0
            parts.append(f"{mins} {'минута' if mins == 1 else 'минуты' if mins < 5 else 'минут'}")

        return " ".join(parts)

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
