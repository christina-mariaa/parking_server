from rest_framework import serializers
from .models import CustomUser, Car, Booking, Payment
from django.utils import timezone
from api.tasks import release_booking_if_not_paid, complete_booking


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
        car = data.get('car')
        user = self.context['request'].user
        if car.user != user:
            raise serializers.ValidationError("You do not have permission to use this car.")
        if Booking.objects.filter(car=car, status='active').exists():
            raise serializers.ValidationError("This car already has an active booking.")
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

        # Запуск фоновой задачи для освобождения брони через 20 минут, если не оплачено
        release_booking_if_not_paid.apply_async((booking.id,), countdown=1200)
        time_to_completion = (booking.end_time - timezone.now()).total_seconds()
        complete_booking.apply_async((booking.id,), countdown=time_to_completion)

        return booking


class PaymentSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'booking', 'amount', 'payment_date']
        read_only_fields = ['id', 'amount', 'payment_date']

    def validate(self, data):
        booking = data['booking']
        if hasattr(booking, 'payment'):
            raise serializers.ValidationError("This booking is already paid.")
        return data

    def create(self, validated_data):
        payment = Payment.objects.create(**validated_data)
        return payment
