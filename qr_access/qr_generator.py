import hmac
import hashlib
import json
import base64
import qrcode
from io import BytesIO
from django.conf import settings


def generate_qr_code(booking_id, start_time, end_time):
    """
    Генерирует QR-код с закодированной информацией о бронировании.

    Данные включают:
    - booking_id: ID бронирования
    - start_time: время начала бронирования (datetime)
    - end_time: время окончания бронирования (datetime)

    Дополнительно данные подписываются с помощью HMAC-SHA256 и секретного ключа,
    чтобы обеспечить целостность и подлинность информации.

    Возвращает:
        Строку в формате base64 PNG изображения, пригодную для вставки в тег <img>.
        Формат строки: "data:image/png;base64,..."
    """
    data = {
        "booking_id": str(booking_id),
        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end_time": end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    signature = hmac.new(
        settings.SIGNATURE_KEY.encode(),
        json.dumps(data, separators=(',', ':')).encode(),
        hashlib.sha256
    ).hexdigest()

    data["signature"] = signature
    data = json.dumps(data, separators=(",", ":"))

    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    byte_data = buffer.getvalue()
    base64_encoded = base64.b64encode(byte_data).decode('utf-8')

    return f"data:image/png;base64,{base64_encoded}"
