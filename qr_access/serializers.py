from rest_framework import serializers


class QRCodeAccessSerializer(serializers.Serializer):
    """
    Сериализатор для проверки доступа по QR-коду.

    Используется в представлении VerifyQRCodeAccessView для начальной проверки структуры запроса.
    """
    booking_id = serializers.CharField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    signature = serializers.CharField()
