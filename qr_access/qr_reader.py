import hmac
import json
import hashlib
from datetime import datetime, timezone
from django.conf import settings
from rest_framework.exceptions import ValidationError
from bookings.models import Booking


def validate_qr_code_data(validated_data):
    """
    Проверяет корректность данных, полученных из QR-кода для доступа к парковке.

    Выполняет следующие проверки:
    - Существование бронирования по переданному booking_id.
    - Наличие оплаты (наличие связанного объекта Payment).
    - Корректность цифровой подписи HMAC (по полям booking_id, start_time, end_time).
    - Актуальность времени: текущее время должно быть между start_time и end_time.

    Аргументы:
        validated_data (dict): Словарь с полями:
            - booking_id (str)
            - start_time (datetime.datetime)
            - end_time (datetime.datetime)
            - signature (str)
    """
    booking_id = str(validated_data['booking_id'])
    start_time = validated_data["start_time"]
    end_time = validated_data["end_time"]
    signature = validated_data["signature"]

    # Проверка, существует ли бронирование
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        raise ValidationError("Бронирование не найдено")

    # Проверка статуса
    if booking.status != 'active':
        raise ValidationError("Бронирование отменено или уже завершено")

    # Проверка оплаты
    if not hasattr(booking, "payment"):
        raise ValidationError("Бронирование не оплачено")

    # Формирование данных без подписи
    unsigned_data = {
        "booking_id": booking_id,
        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end_time": end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    # Формирование подписи на основе поступивших данных
    expected_signature = hmac.new(
        settings.SIGNATURE_KEY.encode(),
        json.dumps(unsigned_data, separators=(",", ":")).encode(),
        hashlib.sha256
    ).hexdigest()

    # Сравнение подписей
    if not hmac.compare_digest(signature, expected_signature):
        raise ValidationError('Подпись не совпадает')

    # Проверка временного интервала
    now = datetime.now(timezone.utc)
    if not (start_time <= now <= end_time):
        raise ValidationError("Время действия бронирования истекло")
