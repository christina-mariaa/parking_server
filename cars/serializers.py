from rest_framework import serializers
from .models import Car


class BaseCarSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для модели Car.
    """
    class Meta:
        model = Car
        fields = ['id', 'license_plate', 'make', 'model', 'color', 'registered_at']
        read_only_fields = ['id', 'registered_at']


class CarSerializer(BaseCarSerializer):
    """
    Сериализатор для работы пользователя со своими автомобилями.

    Дополнительно:
    - Валидация номера автомобиля: нельзя зарегистрировать один и тот же номер повторно у одного пользователя.
    - Автоматически привязывает автомобиль к текущему пользователю при создании.
    """
    def create(self, validated_data):
        """
        Создаёт новый объект Car, привязанный к текущему пользователю.
        """
        user = self.context['request'].user
        return Car.objects.create(user=user, **validated_data)


class AdminCarListSerializer(BaseCarSerializer):
    """
    Сериализатор для отображения автомобилей в админ-панели.

    Дополнительно выводит:
    - user_email: email владельца автомобиля
    - is_deleted: флаг логического удаления
    """
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta(BaseCarSerializer.Meta):
        fields = BaseCarSerializer.Meta.fields + ['user_email', 'is_deleted']
