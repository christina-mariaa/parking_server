from rest_framework import serializers
from django.core.cache import cache
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from cars.serializers import AdminCarListSerializer
from .models import CustomUser
from bookings.models import Booking
from bookings.serializers import AdminBookingListSerializer
from payments.models import Payment
from payments.serializers import AdminPaymentListSerializer
from django.contrib.auth import authenticate
from axes.utils import get_client_ip_address
from axes.helpers import get_client_username
from axes.handlers.proxy import AxesProxyHandler
from rest_framework.exceptions import PermissionDenied


def generate_tokens_for_user(user):
    """
    Генерирует access и refresh токены для переданного пользователя.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Кастомный сериализатор для получения JWT токенов по email и паролю.

    Дополнительно:
    - Проверяется пароль пользователя.
    - В ответ добавляется флаг `is_staff`.
    """
    def validate(self, attrs):
        request = self.context.get('request')
        email = attrs.get('email')
        password = attrs.get('password')

        if AxesProxyHandler.is_locked(request, credentials={'email': email}):
            raise PermissionDenied("Аккаунт временно заблокирован. Повторите позже.")

        user = authenticate(request=request, email=email, password=password)

        if not user:
            raise serializers.ValidationError("Неверный email или пароль.")

        tokens = generate_tokens_for_user(user)
        tokens['is_staff'] = user.is_staff
        return tokens


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.

    Используемые поля: email, пароль, имя, фамилия.
    Пароль передаётся отдельно и не сериализуется в ответе.
    """
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


class UpdateUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления информации о пользователе.
    """
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name']

    def validate_email(self, value):
        user = self.context['request'].user
        if CustomUser.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Этот email уже используется другим пользователем.")
        return value

    def update(self, instance, validated_data):
        old_email = instance.email
        instance = super().update(instance, validated_data)
        new_email = instance.email

        if old_email != new_email:
            cache.delete(old_email)
            cache.set(new_email, instance, timeout=None)

        return instance


class AdminUserListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения краткой информации о пользователях в списке.
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'date_joined', 'is_staff', 'is_deleted']


class AdminUserDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения полной информации о пользователе.

    Дополнительно включает:
    - список автомобилей,
    - список бронирований,
    - список оплат.
    """
    cars = AdminCarListSerializer(many=True)  # Получение автомобилей через related_name='cars'
    bookings = serializers.SerializerMethodField()  # Метод для получения бронирований
    payments = serializers.SerializerMethodField()  # Метод для получения оплат

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'date_joined', 'is_staff',
                  'cars', 'bookings', 'payments']

    def get_bookings(self, obj):
        """
        Получение всех бронирований, связанных с автомобилями пользователя.
        """
        bookings = Booking.objects.filter(car__user=obj).select_related('tariff', 'parking_place')
        return AdminBookingListSerializer(bookings, many=True).data

    def get_payments(self, obj):
        """
        Получение всех оплат, связанных с бронированиями автомобилей пользователя.
        """
        payments = Payment.objects.filter(booking__car__user=obj)
        return AdminPaymentListSerializer(payments, many=True).data


class UpdateAdminStatusSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления флага администратора (is_staff) у пользователя.
    """
    class Meta:
        model = CustomUser
        fields = ['is_staff']

    def validate(self, attrs):
        if 'is_staff' not in attrs:
            raise serializers.ValidationError({"is_staff": "Это поле обязательно для заполнения."})
        return attrs

    def update(self, instance, validated_data):
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)
        instance.save()
        return instance
