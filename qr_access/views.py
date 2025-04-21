import json
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from .qr_generator import generate_qr_code
from .qr_reader import validate_qr_code_data
from .models import QRAccessLog
from .serializers import QRCodeAccessSerializer, QRAccessLogSerializer
from bookings.models import Booking
from .create_log import create_log
from api.permissions import IsAdminPermission


class QRView(APIView):
    """
    Представление для генерации QR-кода, привязанного к конкретному бронированию.

    Доступно только для аутентифицированных пользователей.
    Метод GET принимает идентификатор бронирования (booking_id) и выполняет следующие действия:

    1. Пытается найти бронирование по переданному ID, принадлежащее текущему пользователю.
       Если не найдено — возвращает ошибку 404.
    2. Получает дату и время начала и окончания бронирования.
    3. Генерирует QR-код с закодированными параметрами:
        - ID бронирования
        - start_time
        - end_time
        - подпись HMAC (добавляется в QR для проверки подлинности)
    4. Возвращает сгенерированный QR-код в формате base64-строки PNG-изображения.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, car__user=request.user)
        except Booking.DoesNotExist:
            return Response({"error: Бронирование не найдено"}, status=status.HTTP_404_NOT_FOUND)

        start_time = booking.start_time
        end_time = booking.end_time
        qr = generate_qr_code(booking_id, start_time, end_time)

        return Response(qr, status=status.HTTP_200_OK)


class VerifyQRCodeAccessView(APIView):
    """
    Представление API для проверки доступа по QR-коду.

    Метод POST принимает JSON-данные с информацией о бронировании и подписью:
        - booking_id (str)
        - start_time (str в формате ISO 8601)
        - end_time (str в формате ISO 8601)
        - signature (str)

    Алгоритм работы:
    1. Сериализатор проверяет структуру и типы данных.
    2. Функция validate_qr_code_data проводит основную валидацию:
        - Проверка существования брони.
        - Проверка факта оплаты.
        - Проверка цифровой подписи.
        - Проверка временного интервала действия брони.
    3. В случае успеха возвращает: 200 OK с сообщением "Доступ разрешён".
    4. В случае ошибки возвращает: 403 Forbidden с описанием причины.
    """
    def post(self, request):
        serializer = QRCodeAccessSerializer(data=request.data)
        if serializer.is_valid():
            try:
                validate_qr_code_data(serializer.validated_data)
                return Response({"detail": "Доступ разрешён"}, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({"error": str(e.detail[0])}, status=status.HTTP_403_FORBIDDEN)
        else:
            create_log(
                qr_data=json.dumps(request.data, ensure_ascii=False),
                access_granted=False,
                failure_reason='invalid_format'
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QRAccessLogPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'


class QRAccessLogListView(ListAPIView):
    """
    Представление для получения списка логов попыток доступа по QR-коду.
    """
    queryset = QRAccessLog.objects.all().order_by('-time')
    serializer_class = QRAccessLogSerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]
    pagination_class = QRAccessLogPagination
