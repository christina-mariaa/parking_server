from django.db.models import Q
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


class UserProfileView(APIView):
    """
    Представление для получения, обновления и удаления аккаунта текущим пользователем.

    Поддерживаемые методы:
    - GET: Получить текущий профиль.
    - PATCH: Обновить профиль (например, имя, фамилию, email).
    - DELETE: Удалить аккаунт пользователя (мягкое удаление с проверками).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UpdateUserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        """
        Обновляет профиль пользователя (частично).
        Если обновляется email — обновляет кэш (удаляет старый ключ и сохраняет новый).
        """
        user = request.user
        old_email = user.email
        serializer = UpdateUserSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            new_email = serializer.validated_data.get('email', old_email)

            # Если email изменился — обновляем кэш
            if old_email != new_email:
                cache.delete(old_email)
                cache.set(new_email, user, timeout=None)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """
        Удаляет текущего пользователя.
        Выполняется мягкое удаление (через user.delete()), которое помечает пользователя как неактивного.
        Также удаляется пользователь из кэша.
        """
        user = request.user
        try:
            user.delete()
            cache.delete(user.email)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Аккаунт успешно удалён'}, status=status.HTTP_200_OK)


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
        # Выбор менеджера
        if self.request.query_params.get("hide-deleted", "true").lower() == "true":
            queryset = CustomUser.objects
        else:
            queryset = CustomUser.all_objects

        # Поиск по email
        search_query = self.request.query_params.get("search")
        if search_query:
            queryset = queryset.filter(
                Q(email__icontains=search_query)
            )

        # Подгружаем связанные данные только для retrieve
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                'cars',  # Связанные автомобили
                'cars__bookings',  # Связанные бронирования автомобилей
                'cars__bookings__payment'  # Связанные оплаты бронирований
            )

        return queryset.order_by('id')  # Сортировка по id
    
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
