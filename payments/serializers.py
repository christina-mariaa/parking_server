from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и отображения информации об оплате бронирования.

    Возможности:
    - Проверяет, что бронирование ещё не оплачено (в `validate`).
    - Автоматически устанавливает сумму оплаты (`amount`) на основе тарифа,
      связанного с бронированием (в модели).
    - Поля `amount` и `payment_date` доступны только для чтения.
    """
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'amount', 'payment_date']
        read_only_fields = ['id', 'amount', 'payment_date']

    def validate(self, data):
        booking = data['booking']
        if hasattr(booking, 'payment'):
            raise serializers.ValidationError("Это бронирование уже оплачено.")
        return data

    def create(self, validated_data):
        payment = Payment.objects.create(**validated_data)
        return payment


class AdminPaymentListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения списка оплат в администраторской панели.
    """
    user_email = serializers.ReadOnlyField(source='booking.car.user.email')
    tariff_name = serializers.ReadOnlyField(source='booking.tariff.name')
    booking_id = serializers.ReadOnlyField(source='booking.id')

    class Meta:
        model = Payment
        fields = ['id', 'booking_id', 'user_email', 'tariff_name', 'amount', 'payment_date']
