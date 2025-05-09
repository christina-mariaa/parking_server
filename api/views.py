from rest_framework import status
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ReadOnlyModelViewSet
from .permissions import IsAdminPermission
from .models import CustomUser
from .serializers import (CustomTokenObtainPairSerializer,
                          UserRegistrationSerializer,
                          UpdateUserSerializer,
                          AdminUserListSerializer,
                          AdminUserDetailSerializer,
                          UpdateAdminStatusSerializer)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Представление для получения access и refresh токенов по email и паролю.
    """
    serializer_class = CustomTokenObtainPairSerializer


class UserRegistrationView(APIView):
    """
    Представление для регистрации пользователя.
    """
    permission_classes = []

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Регистрация прошла успешно.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserView(APIView):
    """
    Представление для удаления аккаунта самим пользователем.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        try:
            user.delete()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Аккаунт успешно удалён'}, status=status.HTTP_200_OK)


class UpdateUserView(APIView):
    """
    Представления для обновления информации о пользователе.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        serializer = UpdateUserSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminUserPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdminUserViewSet(ReadOnlyModelViewSet):
    """
    Представление только для чтения списка пользователей и их детальной информации (только для администраторов).

    Поддерживает действия:
    - list: Получить список пользователей.
    - retrieve: Получить подробную информацию по конкретному пользователю.
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


class UpdateAdminStatusView(APIView):
    """
    Представление для обновления прав администратора у пользователя.
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
