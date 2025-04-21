from rest_framework import serializers
from .models import QRAccessLog


class QRCodeAccessSerializer(serializers.Serializer):
    """
    Сериализатор для проверки доступа по QR-коду.

    Используется в представлении VerifyQRCodeAccessView для начальной проверки структуры запроса.
    """
    booking_id = serializers.CharField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    signature = serializers.CharField()


class QRAccessLogSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения списка логов
    """
    class Meta:
        model = QRAccessLog
        fields = '__all__'
