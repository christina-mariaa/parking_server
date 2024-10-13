from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from datetime import timedelta


# Менеджер пользователя
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        if not password:
            raise ValueError("The Password field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Пароль хэшируется на сервере
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# Модель пользователя
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


# Модель автомобиля
class Car(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cars')
    license_plate = models.CharField(max_length=15, unique=True)
    make = models.CharField(max_length=50, blank=True, null=True)  # марка автомобиля
    model = models.CharField(max_length=100, blank=True, null=True)  # модель автомобиля
    color = models.CharField(max_length=50, blank=True, null=True)

    registered_at = models.DateTimeField(auto_now_add=True)  # дата регистрации автомобиля

    def __str__(self):
        return f"{self.license_plate} ({self.make or 'Unknown Make'} {self.model or 'Unknown Model'}) - User: {self.user}"


class Tariff(models.Model):
    DURATION_CHOICES = [
        ('daily', 'Дневной'),  # 1 день
        ('monthly', 'Месячный')  # 30 дней
    ]
    name = models.CharField(max_length=50, choices=DURATION_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # стоимость тарифа

    def get_duration_delta(self):
        if self.name == 'daily':
            return timedelta(days=1)
        elif self.name == 'monthly':
            return timedelta(days=30)
        return timedelta()

    def __str__(self):
        return f"{self.name}"


# Модель парковочного места
class ParkingSpot(models.Model):
    STATUSES = [
        ('booked', 'забронировано'),
        ('available', 'свободно'),
        ('unavailable', 'недоступно для бронирования')
    ]
    spot_number = models.CharField(max_length=10)
    status = models.CharField(max_length=50, choices=STATUSES)

    def __str__(self):
        return f"Парковочное место №{self.spot_number} {self.status}"


class Booking(models.Model):
    STATUSES = [
        ('active', 'Активное'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено')
    ]
    status = models.CharField(max_length=20, choices=STATUSES, default='active')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='bookings')
    parking_place = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE, related_name='bookings')
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField(auto_now_add=True)  # Дата и время начала бронирования
    end_time = models.DateTimeField()  # Дата и время конца бронирования

    def save(self, *args, **kwargs):
        if self.start_time and self.tariff:
            self.end_time = self.start_time + self.tariff.get_duration_delta()
        # Обновляем статус парковочного места на "забронировано"
        self.parking_place.status = 'booked'
        self.parking_place.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # При удалении бронирования меняем статус парковочного места на "доступно"
        self.parking_place.status = 'available'
        self.parking_place.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Бронирование автомобиля {self.car.license_plate} с {self.start_time} по {self.end_time}"


class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    payment_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Автоматически устанавливаем сумму на основе цены тарифа
        self.amount = self.booking.tariff.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Оплата бронирования {self.booking.id}, сумма: {self.amount}"
