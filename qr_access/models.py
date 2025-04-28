from django.db import models
from bookings.models import Booking


class QRAccessLog(models.Model):
    """
    Логирование всех попыток доступа по QR-коду на парковку.

    Сохраняет как успешные, так и неуспешные попытки входа по QR.
    В случае отказа указывается причина из списка предопределённых значений.

    Поля:
        qr_data (TextField): Сырые данные, считанные с QR-кода;
        booking (ForeignKey): Ссылка на бронирование, если удалось распознать;
        access_granted (BooleanField): Флаг, был ли предоставлен доступ;
        failure_reason (CharField): Причина отказа (если доступ не предоставлен);
        time (DateTimeField): Время запроса.
    """
    FAILURE_REASONS = [
        ('booking_not_found', 'Бронирование не найдено'),
        ('booking_unpaid', 'Бронирование не оплачено'),
        ('invalid_signature', 'Подпись не совпадает')
    ]
    qr_data = models.TextField()
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='qr_logs')
    access_granted = models.BooleanField()
    failure_reason = models.CharField(
        choices=FAILURE_REASONS,
        null=True,
        max_length=50
    )
    time = models.DateTimeField(auto_now_add=True)
