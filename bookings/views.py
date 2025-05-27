from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from api.permissions import IsAdminPermission
from .models import Booking
from .serializers import BookingSerializer, AdminBookingListSerializer


class UserBookingView(APIView):
    """
    Представление для пользователя: управление своими бронированиями.

    Методы:
    - GET: возвращает список всех бронирований текущего пользователя.
        Поддерживает фильтрацию по параметрам:
        - `?active=true` — только активные бронирования.
        - `?active=false` — только неактивные бронирования.
        - `?paid=true` — только оплаченные бронирования.
        - `?paid=false` — только неоплаченные бронирования.

    - POST: создание нового бронирования.
        Ожидает поля: car_id, parking_place, tariff_id.
        Проверяет:
        - наличие активного бронирования на автомобиль;
        - доступность выбранного парковочного места.
        В случае успеха возвращает ID созданного бронирования.

    Ограничения:
    - Только авторизованные пользователи могут обращаться к представлению.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Получение списка бронирований пользователя.
        """
        is_active = request.query_params.get('active', None)
        is_paid = request.query_params.get('paid', None)
        bookings = Booking.objects.filter(car__user=request.user)
        if is_active == 'true':
            bookings = bookings.filter(status='active').order_by('-id')
        elif is_active == 'false':
            bookings = bookings.exclude(status='active').order_by('-id')

        if is_paid == 'true':
            # Только оплаченные бронирования
            bookings = bookings.filter(payment__isnull=False).order_by('-id')
        elif is_paid == 'false':
            # Только неоплаченные бронирования
            bookings = bookings.filter(payment__isnull=True).order_by('-id')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
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


class AdminBookingPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdminBookingListView(ListAPIView):
    """
    Представление для получения списка всех бронирований администратором.
    """
    serializer_class = AdminBookingListSerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]
    pagination_class = AdminBookingPagination

    def get_queryset(self):
        """
        Получает список бронирований с фильтрацией по статусу и поиском.

        - Загружает связанные объекты: автомобиль, парковочное место и тариф.
        - Фильтрует по статусу бронирования (?status=active&status=completed).
        - Поддерживает поиск по email пользователя и номеру автомобиля (?search=example).
        - Сортирует бронирования по убыванию ID (сначала новые).
        """
        # Базовый queryset с оптимизированной выборкой связанных объектов
        queryset = Booking.objects.select_related('car', 'parking_place', 'tariff')

        # Фильтрация по статусам (если переданы)
        statuses = self.request.query_params.getlist("status")
        queryset = queryset.filter(status__in=statuses)

        # Фильтрация по email пользователя или номеру автомобиля
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(car__user__email__icontains=search) |
                Q(car__license_plate__icontains=search)
            )

        return queryset.order_by('-id')
