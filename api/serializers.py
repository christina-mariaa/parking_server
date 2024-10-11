from rest_framework import serializers
from .models import CustomUser, Car


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
