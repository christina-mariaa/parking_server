from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.cache import cache


class CustomUserManager(BaseUserManager):
    """
    Менеджер пользователей для модели CustomUser.

    Методы:
    - create_user: создание обычного пользователя.
    - create_superuser: создание суперпользователя (администратора).
    - get_queryset: возвращает только активных (не удалённых) пользователей.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Создаёт и возвращает нового пользователя с указанными email и паролем.
        Email и пароль обязательно должны быть указаны.
        """
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
        """
        Создаёт и возвращает суперпользователя (админа).
        is_staff и is_superuser должны быть установлены в True
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

    def get_queryset(self):
        """
        Возвращает QuerySet, исключающий пользователей с is_deleted=True.
        """
        return super().get_queryset().filter(is_deleted=False)


class CustomUser(AbstractBaseUser):
    """
    Кастомная модель пользователя, основанная на AbstractBaseUser.

    Основные поля:
    - email: уникальный email пользователя (используется как логин)
    - first_name, last_name: имя и фамилия
    - is_active: активность пользователя
    - is_staff: флаг администратора
    - is_superuser: флаг суперпользователя
    - is_deleted: логическое удаление
    - date_joined: дата регистрации

    Методы:
    - delete: логическое удаление пользователя, с проверкой на активные бронирования
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    # Менеджеры
    objects = CustomUserManager()  # Только не удалённые пользователи
    all_objects = models.Manager()  # Все пользователи, включая удалённых

    # Аутентификация по email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def delete(self, *args, **kwargs):
        """
        Логически удаляет пользователя:
        - Проверяет, что у него нет активных бронирований.
        - Деактивирует пользователя.
        - Также логически удаляет все его автомобили.
        """
        if self.cars.filter(bookings__status='active').exists():
            raise Exception("Нельзя удалить пользователя, пока у него есть автомобили с активными бронированиями.")

        self.is_deleted = True
        self.save()

        cache.delete(self.email)

        for car in self.cars.all():
            car.delete()
