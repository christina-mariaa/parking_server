from django.db import models
from api.models import CustomUser


class CarManager(models.Manager):
    """
    Менеджер моделей Car, возвращающий только не удалённые записи.

    Используется по умолчанию в модели Car, чтобы фильтровать записи,
    где is_deleted=False. Это позволяет логически удалять объекты,
    не удаляя их физически из базы данных.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Car(models.Model):
    """
    Модель, представляющая автомобиль, зарегистрированный пользователем.

    Поля:
    - user (ForeignKey): Владелец автомобиля (пользователь системы).
    - license_plate (CharField): Номерной знак автомобиля. Уникален.
    - make (CharField): Марка автомобиля (опционально).
    - model (CharField): Модель автомобиля (опционально).
    - color (CharField): Цвет автомобиля (опционально).
    - is_deleted (BooleanField): Флаг логического удаления. Позволяет сохранять историю, не удаляя запись из БД.
    - registered_at (DateTimeField): Дата и время регистрации автомобиля (устанавливается автоматически).

    Менеджеры:
    - objects: Возвращает только не удалённые записи (is_deleted=False).
    - all_objects: Возвращает все записи, включая логически удалённые.

    Поведение:
    - Метод delete():
        * Выполняет логическое удаление (is_deleted=True).
        * Заменяет license_plate на "Удален" для исключения дубликатов.
        * Если у автомобиля есть активные бронирования — выбрасывается исключение.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cars')
    license_plate = models.CharField(max_length=15, unique=True)
    make = models.CharField(max_length=50, null=True, blank=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)

    objects = CarManager()
    all_objects = models.Manager()

    def delete(self, *args, **kwargs):
        """
        Логическое удаление автомобиля.
        Запрещено, если есть активные бронирования.
        """
        if self.bookings.filter(status='active').exists():
            raise Exception("Нельзя удалить автомобиль, пока на него есть активные бронирования.")
        self.is_deleted = True
        self.license_plate = "Удален"
        self.save()
