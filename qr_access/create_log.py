from .models import QRAccessLog
import json
from django.core.serializers.json import DjangoJSONEncoder


def create_log(qr_data, access_granted, failure_reason=None, booking=None):
    """
    Создаёт запись в QRAccessLog.

    Параметры:
        qr_data (str): Сырые данные из QR-кода.
        booking (Booking | None): Объект бронирования, если удалось найти.
        access_granted (bool): Был ли предоставлен доступ.
        failure_code (str | None): Код причины отказа, если доступ не предоставлен.

    Возвращает:
        QRAccessLog: созданная запись.
    """
    log_entry = QRAccessLog.objects.create(
        qr_data=json.dumps(qr_data, cls=DjangoJSONEncoder, ensure_ascii=False),
        booking=booking,
        access_granted=access_granted,
        failure_reason=failure_reason
    )
    return log_entry
