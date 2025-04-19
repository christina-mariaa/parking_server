from rest_framework import serializers
from .models import ParkingSpot
from bookings.models import Booking


class ParkingSpotSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ParkingSpot.
    """
    class Meta:
        model = ParkingSpot
        fields = ['spot_number', 'status']


class UpdateSpotSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления статуса парковочного места.

    Позволяет изменить только поле `status` у существующего объекта ParkingSpot.
    Ограничения:
    - Нельзя изменить статус, если место уже занято (active booking).
    Методы:
    - update(instance, validated_data): обновляет статус парковочного места и сохраняет изменения.
    """
    class Meta:
        model = ParkingSpot
        fields = ['status']

    def update(self, instance, validated_data):
        # Если у места есть активные бронирования — запретить изменение
        if Booking.objects.filter(parking_place=instance, status='active').exists():
            raise serializers.ValidationError("Нельзя изменить статус: место связано с активным бронированием.")

        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance
