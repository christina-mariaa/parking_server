from asgiref.sync import async_to_sync
from rest_framework import serializers
from cars.models import Car
from tariffs.models import Tariff
from parking_spots.models import ParkingSpot
from .models import Booking
from realtime.notifications.bookings import notify_users_about_booking_change


class BaseBookingSerializer(serializers.ModelSerializer):
    """
        Базовый сериализатор для отображения информации о бронировании.

        Содержит общие поля, используемые как пользователями, так и администраторами:
        - id.
        - Статус.
        - Дату и время начала бронирования.
        - Дату и время конца бронирования.
        - Название тарифа.
        - Номер парковочного места.
        - Номер автомобиля.
        - Информация об оплате (сумма и дата, если есть).

        Поля status, start_time и end_time доступны только для чтения.
        """
    tariff_name = serializers.ReadOnlyField(source='tariff.name')
    parking_place = serializers.ReadOnlyField(source='parking_place.spot_number')
    car_license_plate = serializers.ReadOnlyField(source='car.license_plate')

    # Поля, получаемые через метод — информация об оплате
    payment_amount = serializers.SerializerMethodField(read_only=True)
    payment_date = serializers.SerializerMethodField(read_only=True)

    def get_payment_amount(self, obj):
        """
        Получает сумму оплаты, если она есть.
        """
        return obj.payment.amount if hasattr(obj, 'payment') else None

    def get_payment_date(self, obj):
        """
        Получает дату оплаты, если она есть.
        """
        return obj.payment.payment_date if hasattr(obj, 'payment') else None

    class Meta:
        model = Booking
        fields = ['id', 'status',
                  'start_time', 'end_time',
                  'tariff_name', 'parking_place', 'car_license_plate', 'payment_amount', 'payment_date']
        read_only_fields = ['status', 'start_time', 'end_time']


class BookingSerializer(BaseBookingSerializer):
    """
    Сериализатор для пользователя.

    Позволяет:
    - Просматривать подробную информацию о бронировании.
    - Создавать новое бронирование, указывая:
        * ID автомобиля (`car_id`)
        * ID тарифа (`tariff_id`)
        * Парковочное место (`parking_place`)
    Также отображаются данные автомобиля:
    - Марка, модель, цвет (только для чтения).

    Выполняет валидацию:
    - Нельзя бронировать автомобиль, если на него уже есть активное бронирование.
    - Место должно быть свободным.
    """
    # Отображаемые поля, взятые из связанной модели Car
    car_make = serializers.CharField(source='car.make', read_only=True)
    car_model = serializers.CharField(source='car.model', read_only=True)
    car_color = serializers.CharField(source='car.color', read_only=True)

    # Поля, используемые при создании бронирования
    parking_place_id = serializers.PrimaryKeyRelatedField(
        queryset=ParkingSpot.objects.all(), source='parking_place', write_only=True
    )
    car_id = serializers.PrimaryKeyRelatedField(
        queryset=Car.objects.all(), source='car', write_only=True
    )
    tariff_id = serializers.PrimaryKeyRelatedField(
        queryset=Tariff.objects.all(), source='tariff', write_only=True
    )

    class Meta(BaseBookingSerializer.Meta):
        fields = BaseBookingSerializer.Meta.fields + ['car_id',  'car_make', 'car_model', 'car_color',
                                                      'tariff_id', 'parking_place_id']

    def validate(self, data):
        """
        Валидация данных при создании бронирования:
        - Проверяет, есть ли уже активное бронирование на этот автомобиль.
        - Проверяет, доступно ли выбранное парковочное место.
        """
        car = data.get('car')
        user = self.context['request'].user

        # Автомобиль должен принадлежать пользователю
        if car.user != user:
            raise serializers.ValidationError("Вы не можете бронировать чужой автомобиль.")

        # Проверка наличия активного бронирования на автомобиль
        if Booking.objects.filter(car=car, status='active').exists():
            raise serializers.ValidationError("На этот автомобиль уже есть активное бронирование")
        parking_place = data.get('parking_place')

        # Проверка доступности парковочного места
        if parking_place.status != 'available':
            raise serializers.ValidationError("Выбранное место недоступно")
        return data

    def create(self, validated_data):
        """
        Создание нового бронирования. Время окончания устанавливается в модели.
        """
        booking = Booking(**validated_data)
        booking.save()
        return booking


class AdminBookingListSerializer(BaseBookingSerializer):
    """
    Сериализатор для администратора. Только для чтения.

    Дополнительно отображает:
    - Email пользователя, которому принадлежит автомобиль.
    """
    user_email = serializers.ReadOnlyField(source='car.user.email')

    class Meta(BaseBookingSerializer.Meta):
        fields = BaseBookingSerializer.Meta.fields + ['user_email']
