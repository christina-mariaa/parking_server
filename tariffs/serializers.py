from rest_framework import serializers
from .models import Tariff, TariffPriceHistory


class TariffSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения тарифов обычным пользователям.
    Исключает служебные поля created_at и updated_at.
    """
    class Meta:
        model = Tariff
        fields = ['id', 'name', 'price']


class AdminTariffSerializer(serializers.ModelSerializer):
    """
    Сериализатор для администратора: включает все поля.
    """
    class Meta:
        model = Tariff
        fields = ['id', 'name', 'price', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        price = data.get('price')
        if price < 0:
            raise serializers.ValidationError("Цена не может быть отрицательной")
        return data


class UpdateTariffSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления только цены тарифа.
    Используется в PATCH-запросах.
    """
    class Meta:
        model = Tariff
        fields = ['price']

    def validate(self, data):
        price = data.get('price')
        if price < 0:
            raise serializers.ValidationError("Цена не может быть отрицательной")
        return data

    def update(self, instance, validated_data):
        """
        Обновляет цену тарифа и фиксирует пользователя, который её изменил.
        """
        user = self.context['request'].user  # Получаем текущего пользователя из контекста
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save(changed_by=user)  # Передаём changed_by при сохранении
        return instance


class TariffPriceHistorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения истории изменения цен тарифов.
    """
    tariff = serializers.CharField(source='tariff.name', read_only=True)
    changed_by = serializers.CharField(source='changed_by.email', read_only=True)

    class Meta:
        model = TariffPriceHistory
        fields = ['tariff', 'old_price', 'new_price', 'changed_by', 'changed_at']
