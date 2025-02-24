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

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


# Модель пользователя
class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    objects = CustomUserManager()
    all_objects = models.Manager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def delete(self, *args, **kwargs):
        # Проверим, есть ли связанные автомобили с активными бронированиями
        if self.cars.filter(bookings__status='active').exists():
            raise Exception("Нельзя удалить пользователя, пока у него есть автомобили с активными бронированиями.")

        self.is_active = False
        self.save()

        # Обновим связанные автомобили
        for car in self.cars.all():
            car.delete()


class CarManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


# Модель автомобиля
class Car(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cars')
    license_plate = models.CharField(max_length=15)
    make = models.CharField(max_length=50, null=True)  # марка автомобиля
    model = models.CharField(max_length=100, null=True)  # модель автомобиля
    color = models.CharField(max_length=50, null=True)
    is_deleted = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)  # дата регистрации автомобиля
    objects = CarManager()
    all_objects = models.Manager()

    def delete(self, *args, **kwargs):
        if self.bookings.filter(status='active').exists():
            raise Exception("Нельзя удалить автомобиль, пока на него есть активные бронирования.")
        self.is_deleted = True
        self.license_plate = "Удален"
        self.save()


class Tariff(models.Model):
    DURATION_CHOICES = [
        ('daily', 'Дневной'),  # 1 день
        ('monthly', 'Месячный')  # 30 дней
    ]
    name = models.CharField(max_length=50, choices=DURATION_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Стоимость тарифа
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания
    updated_at = models.DateTimeField(auto_now=True)  # Дата последнего изменения

    def get_duration_delta(self):
        """Возвращает длительность действия тарифа в днях."""
        if self.name == 'daily':
            return timedelta(days=1)
        elif self.name == 'monthly':
            return timedelta(days=30)
        return timedelta()


# Модель парковочного места
class ParkingSpot(models.Model):
    STATUSES = [
        ('booked', 'забронировано'),
        ('available', 'свободно'),
        ('unavailable', 'недоступно для бронирования')
    ]
    spot_number = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=50, choices=STATUSES)


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
        if not self.pk and self.start_time and self.tariff:  # Проверяем, что объект ещё не сохранён
            self.end_time = self.start_time + self.tariff.get_duration_delta()
        super().save(*args, **kwargs)


class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    payment_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Автоматически устанавливаем сумму на основе цены тарифа
        self.amount = self.booking.tariff.price
        super().save(*args, **kwargs)


class ParkingMap(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название карты")
    svg_file = models.FileField(upload_to='parking_maps/', verbose_name="Файл SVG")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
