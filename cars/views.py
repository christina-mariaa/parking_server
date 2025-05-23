from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .models import Car
from .serializers import CarSerializer, AdminCarListSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from api.permissions import IsAdminPermission


class UserCarListCreateView(APIView):
    """
    Представление для получения и создания автомобилей пользователя.

    Методы:
    - GET: Возвращает список автомобилей текущего пользователя.
        - Если передан параметр ?free=true, исключаются авто с активными бронированиями.
    - POST: Создаёт новый автомобиль, привязанный к текущему пользователю.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        is_free = request.query_params.get('free', None)
        if is_free == 'true':
            cars = Car.objects.filter(user=request.user).exclude(bookings__status='active')
        else:
            cars = Car.objects.filter(user=request.user)

        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CarSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCarDeleteView(APIView):
    """
    Представление для логического удаления автомобиля пользователя.

    Метод:
    - DELETE: Удаляет автомобиль, если нет активных бронирований.

    Параметры:
        car_id (int): ID удаляемого автомобиля.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, car_id):
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


class AdminCarPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdminCarListView(ListAPIView):
    """
    Представление для администратора: чтение списка всех автомобилей.
    Особенности:
    - Показывает как активные, так и удалённые автомобили.
    - Поддерживается пагинация (20 объектов на страницу).
    """
    serializer_class = AdminCarListSerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]
    pagination_class = AdminCarPagination

    def get_queryset(self):
        """
        Возвращает отфильтрованный список автомобилей на основе параметров поиска.
        """
        if self.request.query_params.get('hide-deleted', 'true').lower() == 'true':
            queryset = Car.objects.select_related('user')
        else:
            queryset = Car.all_objects.select_related('user')

        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(license_plate__icontains=search_query) |
                Q(user__email__icontains=search_query)
            )

        return queryset.order_by('id')
