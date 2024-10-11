from rest_framework import serializers
from .models import CustomUser, Car, Booking
from django.utils import timezone
from api.tasks import release_booking_if_not_paid


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.is_active = False  # Сначала пользователь не активен
        user.save()
        return user


class CarSerializer(serializers.ModelSerializer):

    class Meta:
        model = Car
        fields = ['id', 'license_plate', 'make', 'model', 'color', 'registered_at']
        read_only_fields = ['registered_at']

    def create(self, validated_data):
        user = self.context['request'].user
        car = Car.objects.create(user=user, **validated_data)
        return car


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'status', 'car', 'parking_place', 'tariff', 'start_time', 'end_time']
        read_only_fields = ['status', 'start_time', 'end_time']

    def validate(self, data):
        parking_place = data.get('parking_place')
        if parking_place.status != 'available':
            raise serializers.ValidationError("The selected parking spot is not available.")
        return data

    def create(self, validated_data):
        car = validated_data['car']
        parking_place = validated_data['parking_place']
        tariff = validated_data['tariff']

        booking = Booking.objects.create(
            car=car,
            parking_place=parking_place,
            tariff=tariff,
            start_time=timezone.now(),
        )

        # Запускаем фоновую задачу для освобождения брони через 20 минут, если не оплачено
        # release_booking_if_not_paid.apply_async((booking.id,), countdown=1200)

        return booking
