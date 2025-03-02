from rest_framework import serializers
from .models import CustomUser, Car, Booking, Payment, Tariff, ParkingSpot, ParkingMap
from django.utils import timezone
from django.core.cache import cache
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

def get_user_from_cache(email):
    user = cache.get(email)
    if not user:
        try:
            user = CustomUser.objects.get(email=email)
            cache.set(email, user, timeout=None)
        except CustomUser.DoesNotExist:
            return None
    return user


def generate_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = get_user_from_cache(email)
        if not user or not user.check_password(password):
            raise serializers.ValidationError("Неверный email или пароль.")

        if not user.is_active:
            raise serializers.ValidationError("Пользователь не активен.")

        tokens = generate_tokens_for_user(user)
        tokens['is_staff'] = user.is_staff
        return tokens


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
        return user


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id', 'license_plate', 'make', 'model', 'color']
        read_only_fields = ['registered_at']

    def validate_license_plate(self, value):
        if Car.objects.filter(license_plate=value, is_deleted=False).exists():
            raise serializers.ValidationError("Автомобиль с таким номером уже существует.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        car = Car.objects.create(user=user, **validated_data)
        return car


class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = ['id', 'name', 'price']


class BookingSerializer(serializers.ModelSerializer):
    car_license_plate = serializers.CharField(source='car.license_plate', read_only=True)
    car_make = serializers.CharField(source='car.make', read_only=True)
    car_model = serializers.CharField(source='car.model', read_only=True)
    car_color = serializers.CharField(source='car.color', read_only=True)
    tariff_name = serializers.CharField(source='tariff.name', read_only=True)
    car_id = serializers.PrimaryKeyRelatedField(
        queryset=Car.objects.all(), source='car', write_only=True
    )
    tariff_id = serializers.PrimaryKeyRelatedField(
        queryset=Tariff.objects.all(), source='tariff', write_only=True
    )
    payment_amount = serializers.SerializerMethodField()
    payment_date = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'status', 'car_id', 'car_license_plate', 'car_make', 'car_model', 'car_color',
            'parking_place', 'tariff_id', 'tariff_name', 'start_time', 'end_time', 'payment_amount', 'payment_date'
        ]
        read_only_fields = ['status', 'start_time', 'end_time']

    def get_payment_amount(self, obj):
        """Возвращает сумму оплаты, если она существует."""
        return obj.payment.amount if hasattr(obj, 'payment') else None

    def get_payment_date(self, obj):
        """Возвращает дату оплаты, если она существует."""
        return obj.payment.payment_date if hasattr(obj, 'payment') else None

    def validate(self, data):
        car = data.get('car')
        user = self.context['request'].user
        # Проверка: активное бронирование на автомобиль
        if Booking.objects.filter(car=car, status='active').exists():
            raise serializers.ValidationError("На этот автомобиль уже есть активное бронирование")
        parking_place = data.get('parking_place')
        # Проверка: доступность выбранного места
        if parking_place.status != 'available':
            raise serializers.ValidationError("Выбранное место недоступно")
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
            raise serializers.ValidationError("Это бронирование уже оплачено.")
        return data

    def create(self, validated_data):
        payment = Payment.objects.create(**validated_data)
        return payment


class ParkingSpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSpot
        fields = ['spot_number', 'status']


class ParkingMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingMap
        fields = ['id', 'name', 'svg_file', 'uploaded_at']


class AdminCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id', 'license_plate', 'make', 'model', 'color', 'registered_at']


# Сериализатор для бронирований
class AdminBookingSerializer(serializers.ModelSerializer):
    tariff_name = serializers.ReadOnlyField(source='tariff.name')
    parking_place = serializers.ReadOnlyField(source='parking_place.spot_number')
    car_license_plate = serializers.ReadOnlyField(source='car.license_plate')
    class Meta:
        model = Booking
        fields = ['id', 'status', 'start_time', 'end_time', 'tariff_name', 'parking_place', 'car_license_plate']


# Сериализатор для оплат
class AdminPaymentSerializer(serializers.ModelSerializer):
    booking_id = serializers.ReadOnlyField(source='booking.id')
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'payment_date', 'booking_id']


# Сериализатор для пользователя
class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff', 'is_deleted']


# Сериализатор для детализированной информации о пользователе
class AdminUserDetailSerializer(serializers.ModelSerializer):
    cars = AdminCarSerializer(many=True)  # Получение автомобилей через related_name='cars'
    bookings = serializers.SerializerMethodField()  # Метод для получения бронирований
    payments = serializers.SerializerMethodField()  # Метод для получения оплат

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff', 'cars', 'bookings', 'payments']

    def get_bookings(self, obj):
        # Получение всех бронирований через автомобили пользователя
        bookings = Booking.objects.filter(car__user=obj).select_related('tariff', 'parking_place')
        return AdminBookingSerializer(bookings, many=True).data

    def get_payments(self, obj):
        # Получение всех оплат через бронирования автомобилей пользователя
        payments = Payment.objects.filter(booking__car__user=obj)
        return AdminPaymentSerializer(payments, many=True).data


class AdminBookingListSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='car.user.email')
    car_license_plate = serializers.ReadOnlyField(source='car.license_plate')
    tariff_name = serializers.ReadOnlyField(source='tariff.name')
    class Meta:
        model = Booking
        fields = ['id', 'status', 'car_license_plate', 'user_email', 'parking_place', 'start_time', 'end_time', 'tariff_name', 'user_email']


class AdminPaymentListSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='booking.car.user.email')
    tariff_name = serializers.ReadOnlyField(source='booking.tariff.name')
    booking_id = serializers.ReadOnlyField(source='booking.id')
    class Meta:
        model = Payment
        fields = ['id', 'booking_id', 'user_email', 'tariff_name', 'amount', 'payment_date']


class AdminCarListSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    class Meta:
        model = Car
        fields = ['id', 'license_plate', 'make', 'model', 'color', 'user_email', 'registered_at', 'is_deleted']


class UpdateAdminStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['is_staff']

    def update(self, instance, validated_data):
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)
        instance.save()
        return instance


class AdminTariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = ['id', 'name', 'price', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UpdateTariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = ['price']

    def update(self, instance, validated_data):
        instance.price = validated_data.get('price', instance.price)
        instance.save()
        return instance


class UpdateSpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSpot
        fields = ['status']

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance