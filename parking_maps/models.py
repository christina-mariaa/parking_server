from django.db import models
from api.models import CustomUser


class ParkingMap(models.Model):
    """
    Модель, представляющая загруженную SVG-карту парковки.

    Используется для визуального отображения расположения парковочных мест на клиенте.

    Атрибуты:
        name (str): Название карты.
        description (str, optional): Дополнительное описание карты.
        svg_file (File): Загружаемый SVG-файл с изображением карты.
        uploaded_by (CustomUser): Пользователь, загрузивший карту. Может быть null, если пользователь удалён.
        uploaded_at (datetime): Дата и время загрузки карты.
    """
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500, null=True, blank=True)
    svg_file = models.FileField(upload_to='parking_maps/')
    uploaded_by = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL, related_name='maps')
    uploaded_at = models.DateTimeField(auto_now_add=True)
