from rest_framework import serializers
from .models import Tariff, TariffPriceHistory


class TariffSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения тарифов обычным пользователям.

    Поля:
        - id: Идентификатор тарифа.
        - name: Название тарифа.
        - price: Стоимость тарифа.
        - duration_display: Человекопонятная длительность (например, "2 часа").
    """
    duration_display = serializers.SerializerMethodField()

    class Meta:
        model = Tariff
        fields = ['id', 'name', 'price', 'duration_display']

    def get_duration_display(self, obj):
        return obj.duration_display


class AdminTariffSerializer(serializers.ModelSerializer):
    """
    Сериализатор для администратора: включает все поля.
    """
    duration_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Tariff
        fields = ['id', 'name', 'price', 'duration_minutes', 'duration_display', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'duration_display']

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Цена не может быть отрицательной")
        return value

    def validate_duration_minutes(self, value):
        if value <= 0:
            raise serializers.ValidationError("Длительность должна быть положительной")
        return value

    def get_duration_display(self, obj):
        return obj.duration_display


class UpdateTariffSerializer(serializers.ModelSerializer):
    """
    Сериализатор для частичного обновления тарифа администратором.

    Позволяет обновить цену и/или статус активности.
    Фиксирует пользователя, изменившего цену, в истории.
    """
    class Meta:
        model = Tariff
        fields = ['price', 'is_active']

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Цена не может быть отрицательной")
        return value

    def update(self, instance, validated_data):
        """
        Обновляет цену тарифа и фиксирует пользователя, который её изменил.
        """
        user = self.context['request'].user  # Получаем текущего пользователя из контекста
        price_changed = 'price' in validated_data and validated_data['price'] != instance.price

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Сохраняем с передачей changed_by только если цена изменилась
        if price_changed:
            instance.save(changed_by=user)
        else:
            instance.save()

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
