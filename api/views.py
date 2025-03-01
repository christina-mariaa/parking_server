from django.http import HttpResponse
from django.db import models
from django.db.models import Count, Case, When, Sum
from django.utils.timezone import now, timedelta
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser
import datetime
import re
import os

from .models import (
    CustomUser,
    Car,
    Tariff,
    Booking,
    Payment,
    ParkingSpot,
    ParkingMap,
)
from .serializers import *
from .permissions import IsAdminPermission


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserRegistrationView(APIView):
    """
    Представление для регистрации пользователя.
    """
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Регистрация прошла успешно.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Получение списка автомобилей пользователя.
        """
        is_free = request.query_params.get('free', None)

        if is_free == 'true':
            # Получение списка автомобилей без активных бронирований
            cars = Car.objects.filter(user=request.user).exclude(
                bookings__status='active'
            )
        else:
            # Получение всех автомобилей пользователя
            cars = Car.objects.filter(user=request.user)

        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Создание нового автомобиля пользователем.
        """
        serializer = CarSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, car_id, *args, **kwargs):
        """
        Удаление автомобиля пользователем.
        """
        try:
            car = Car.objects.get(id=car_id, user=request.user, is_deleted=False)
            if car.bookings.filter(status='active').exists():
                return Response(
                    {"error": "Нельзя удалить автомобиль с активными бронированиями."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            car.delete()
            return Response({"message": "Автомобиль успешно удалён."}, status=status.HTTP_200_OK)
        except Car.DoesNotExist:
            return Response({"error": "Автомобиль не найден или уже удалён."}, status=status.HTTP_404_NOT_FOUND)


class UserBookingView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        """
        Получение списка бронирований пользователя.
        """
        is_active = request.query_params.get('active', None)
        is_paid = request.query_params.get('paid', None)
        bookings = Booking.objects.filter(car__user=request.user)
        if is_active == 'true':
            bookings = bookings.filter(status='active')

        if is_paid == 'true':
            # Только оплаченные бронирования
            bookings = bookings.filter(payment__isnull=False)
        elif is_paid == 'false':
            # Только неоплаченные бронирования
            bookings = bookings.filter(payment__isnull=True)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Создание бронирования пользователем.
        """
        serializer = BookingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            booking = serializer.save()
            return Response({
                'message': 'Бронирование успешно создано.',
                'booking_id': booking.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Получение списка оплат пользователя.
        """
        payments = Payment.objects.filter(booking__car__user=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Создание новой оплаты для указанного бронирования.
        """
        booking_id = kwargs.get('booking_id')
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Бронирование не найдено."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PaymentSerializer(data={'booking': booking.id})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_color_by_status(status):
    colors = {
        'available': '#99CB62',
        'booked': '#F09686',
        'unavailable': '#EEEEB9'
    }
    return colors.get(status, '#FFFFFF')


def generate_svg_with_status():
    """
    Генерирует SVG с раскраской парковочных мест в зависимости от их статуса.
    """
    latest_map = ParkingMap.objects.latest('uploaded_at')
    svg_content = latest_map.svg_file.read().decode('utf-8')
    parking_spots = ParkingSpot.objects.all()
    for spot in parking_spots:
        color = get_color_by_status(spot.status)
        spot_id = f'Rectangle {spot.spot_number}'

        reg_exp = re.compile(rf'<rect[^>]*id="{spot_id}"[^>]*fill="[^"]*"', re.DOTALL)

        svg_content = re.sub(
            reg_exp,
            lambda match: match.group(0).replace(re.search(r'fill="[^"]*"',
                                                           match.group(0)).group(), f'fill="{color}"'),
            svg_content
        )

    return svg_content


class LatestParkingMapView(APIView):
    """
    Представление для получения карты парковки.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        svg_with_status = generate_svg_with_status()
        return Response({"svg_content": svg_with_status}, status=status.HTTP_200_OK)


class TariffsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tariffs = Tariff.objects.all()
        serializer = TariffSerializer(tariffs, many=True)
        return Response(serializer.data)


class AdminUserPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdminUserViewSet(ReadOnlyModelViewSet):
    """
    Представление для получения списка пользователей и детальной информации о пользователе администратором.
    """
    permission_classes = [IsAuthenticated, IsAdminPermission]
    pagination_class = AdminUserPagination
    
    def get_queryset(self):
        return CustomUser.all_objects.prefetch_related(
            'cars',  # Связанные автомобили
            'cars__bookings',  # Связанные бронирования автомобилей
            'cars__bookings__payment'  # Связанные оплаты бронирований
        ).order_by('id')  # Сортировка по id
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AdminUserListSerializer  # Сериализатор для списка пользователей
        if self.action == 'retrieve':
            return AdminUserDetailSerializer  # Сериализатор для детальной информации


class AdminBookingPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdminBookingViewSet(ReadOnlyModelViewSet):
    """
    Представление для получения списка всех бронирований администратором.
    """
    queryset = Booking.objects.select_related('car', 'parking_place', 'tariff').order_by('id')
    serializer_class = AdminBookingListSerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]
    pagination_class = AdminBookingPagination


class AdminPaymentPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdminPaymentViewSet(ReadOnlyModelViewSet):
    """
    Представление для получения списка всех оплат администратором.
    """
    queryset = Payment.objects.select_related('booking__car__user', 'booking__tariff').order_by('id')
    serializer_class = AdminPaymentListSerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]
    pagination_class = AdminPaymentPagination


class AdminCarPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdminCarViewSet(ReadOnlyModelViewSet):
    """
    Представление для получения списка всех автомобилей администратором.
    """
    queryset = Car.all_objects.select_related('user').order_by('id')
    serializer_class = AdminCarListSerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]
    pagination_class = AdminCarPagination


class UpdateAdminStatusView(APIView):
    """
    Представление для назначения пользователю прав администратора.
    """
    permission_classes = [IsAuthenticated, IsAdminPermission]

    def patch(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateAdminStatusSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Статус админа успешно обновлен"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TariffView(APIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]

    def get(self, request, *args, **kwargs):
        """
        Получение списка тарифов администратором.
        """
        tariffs = Tariff.objects.all().order_by('id')
        serializer = AdminTariffSerializer(tariffs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Создание нового тарифа администратором.
        """
        serializer = AdminTariffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        """
        Обновление существующего тарифа администратором.
        """
        tariff_id = kwargs.get('tariff_id')
        try:
            tariff = Tariff.objects.get(id=tariff_id)
        except Tariff.DoesNotExist:
            return Response({"error": "Тариф не найден"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateTariffSerializer(tariff, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Тариф успешно обновлен", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ParkingSpotView(APIView):
    def get_permissions(self):
        """
        Динамическое назначение разрешений для разных операций.
        """
        if self.request.method == 'GET':
            # Для получения списка мест разрешены запросы без прав администратора
            return [IsAuthenticated()]
        # Для всех остальных операций требуется авторизация администратора
        return [IsAuthenticated(), IsAdminPermission()]

    def get(self, request):
        """
        Получение списка всех парковочных мест.
        """
        parking_spots = ParkingSpot.objects.all().order_by('spot_number')
        serializer = ParkingSpotSerializer(parking_spots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Создание нового парковочного места администратором.
        """
        spot_number = request.data.get("spot_number")
        status = request.data.get("status", "available")  # По умолчанию статус - "available"

        if status not in ["available", "unavailable"]:
            return Response({"error": "Неверный статус. Допустимы только 'available' или 'unavailable'."}, status=400)

        if not spot_number:
            return Response({"error": "Номер места обязателен."}, status=400)

        if ParkingSpot.objects.filter(spot_number=spot_number).exists():
            return Response({"error": f"Место с номером {spot_number} уже существует."}, status=400)

        spot = ParkingSpot.objects.create(spot_number=spot_number, status=status)
        return Response(ParkingSpotSerializer(spot).data, status=201)

    def patch(self, request, spot_number):
        """
        Обновление статуса парковочного места администратором.
        """
        try:
            spot = ParkingSpot.objects.get(spot_number=spot_number)
        except ParkingSpot.DoesNotExist:
            return Response({"error": "Место не найдено"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateSpotSerializer(spot, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Статус места успешно обновлен", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, spot_number):
        """
        Удаление парковочного места администратором.
        """
        try:
            spot = ParkingSpot.objects.get(spot_number=spot_number)

            # Проверяем, есть ли активные бронирования для этого места
            if Booking.objects.filter(parking_place=spot, status='active').exists():
                return Response({"error": f"Место {spot_number} не может быть удалено, так как оно забронировано."},
                                status=400)

            # Удаляем парковочное место
            spot.delete()
            return Response({"detail": f"Парковочное место {spot_number} успешно удалено."}, status=200)
        except ParkingSpot.DoesNotExist:
            return Response({"error": f"Парковочное место {spot_number} не найдено."}, status=404)


class BulkCreateParkingSpotsView(APIView):
    """
    Представление для массового добавления парковочных мест администратором.
    """
    permission_classes = [IsAuthenticated, IsAdminPermission]

    def post(self, request):
        if not isinstance(request.data, list):
            return Response({"error": "Ожидался список объектов для добавления."}, status=status.HTTP_400_BAD_REQUEST)

        errors = []
        created_spots = []

        for spot_data in request.data:
            spot_number = spot_data.get("spot_number")
            status = spot_data.get("status", "available")

            if not spot_number:
                errors.append({"spot_number": None, "error": "Номер места обязателен."})
                continue

            if status not in ["available", "unavailable"]:
                errors.append({"spot_number": spot_number, "error": "Недопустимый статус."})
                continue

            if ParkingSpot.objects.filter(spot_number=spot_number).exists():
                errors.append({"spot_number": spot_number, "error": "Место с таким номером уже существует."})
                continue

            # Создание парковочного места
            spot = ParkingSpot.objects.create(spot_number=spot_number, status=status)
            created_spots.append(spot)

        created_spots_serialized = ParkingSpotSerializer(created_spots, many=True).data

        return Response({
            "created": created_spots_serialized,
            "errors": errors
        }, status=207)


class UploadParkingMapView(APIView):
    """
    Добавление карты парковки в формате SVG администратором.
    """
    permission_classes = [IsAuthenticated, IsAdminPermission]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = ParkingMapSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ParkingStatusSummaryView(APIView):
    """
    Получение статистики по статусам мест администратором.
    """
    permission_classes = [IsAuthenticated, IsAdminPermission]

    def get(self, request):
        status_counts = ParkingSpot.objects.values('status').annotate(count=Count('status'))
        result = {item['status']: item['count'] for item in status_counts}
        return Response(result)


class BookingStatsByTariffView(APIView):
    """
    Получение статистики по бронированиям за день, неделю, месяц администратором.
    """
    permission_classes = [IsAuthenticated, IsAdminPermission]

    def get(self, request, *args, **kwargs):
        # Текущее время
        today = now()

        # Периоды для статистики
        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_week = start_of_day - timedelta(days=start_of_day.weekday())  # Понедельник текущей недели
        start_of_month = start_of_day.replace(day=1)  # Первое число текущего месяца
        start_of_year = today.replace(month=1, day=1)  # Первое января текущего года

        periods = {
            "day": start_of_day,
            "week": start_of_week,
            "month": start_of_month,
            "year": start_of_year,
        }

        # Словарь для хранения данных статистики
        stats = {}
        for period_name, start_time in periods.items():
            data = (
                Booking.objects.filter(start_time__gte=start_time)
                .values("tariff__name")
                .annotate(
                    count=Count("id"),  # Общее количество бронирований
                    unpaid_count=Count(  # Количество неоплаченных бронирований
                        Case(
                            When(payment__isnull=True, then=1),  # Условие: если оплаты нет
                            output_field=models.IntegerField(),
                        )
                    ),
                )
            )
            stats[period_name] = list(data)

        return Response(stats)
