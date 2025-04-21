import hmac
import json
import hashlib
from datetime import datetime, timezone
from django.conf import settings
from rest_framework.exceptions import ValidationError
from bookings.models import Booking
from .create_log import create_log


def validate_qr_code_data(validated_data):
    """
    Выполняет полную проверку данных из QR-кода для доступа и логирует результат.

    Проверки включают:
    - Существование бронирования.
    - Статус бронирования (должно быть активным).
    - Наличие оплаты.
    - Корректность HMAC-подписи.
    - Актуальность временного интервала.

    В случае отказа создаёт запись в QRAccessLog с соответствующей причиной.
    При успешной проверке также создаётся лог успешного доступа.

    Аргументы:
        validated_data (dict): Данные, прошедшие сериализатор. Ожидаются поля:
            - booking_id (str)
            - start_time (datetime)
            - end_time (datetime)
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
        create_log(validated_data, access_granted=False, failure_reason='booking_not_found')
        raise ValidationError("Бронирование не найдено")

    # Проверка статуса
    if booking.status != 'active':
        create_log(validated_data, access_granted=False, failure_reason='booking_inactive', booking=booking)
        raise ValidationError("Бронирование отменено или уже завершено")

    # Проверка оплаты
    if not hasattr(booking, "payment"):
        create_log(validated_data, access_granted=False, failure_reason='booking_unpaid', booking=booking)
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
        create_log(validated_data, access_granted=False, failure_reason='invalid_signature', booking=booking)
        raise ValidationError('Подпись не совпадает')

    # Проверка временного интервала
    now = datetime.now(timezone.utc)
    if not (start_time <= now <= end_time):
        create_log(validated_data, access_granted=False, failure_reason='expired', booking=booking)
        raise ValidationError("Время действия бронирования истекло")

    create_log(validated_data, access_granted=True, booking=booking)
