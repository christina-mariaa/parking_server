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
    failure_reason_display = serializers.SerializerMethodField()

    class Meta:
        model = QRAccessLog
        fields = ['id', 'qr_data', 'access_granted', 'failure_reason', 'failure_reason_display', 'time', 'booking']

    def get_failure_reason_display(self, obj):
        return obj.get_failure_reason_display() if obj.failure_reason else None
