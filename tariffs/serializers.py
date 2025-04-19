from rest_framework import serializers
from .models import Tariff


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
