from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from api.permissions import IsAdminPermission
from .models import SupportRequest
from .serializers import (
    SupportRequestSerializer,
    SupportReplySerializer,
)
from django.shortcuts import get_object_or_404


class SupportRequestListCreateAPIView(APIView):
    """
    API для работы с обращениями пользователя в техподдержку.

    GET:
    - Возвращает все обращения пользователя.
    POST:
    - Создаёт новое обращение от текущего пользователя.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        requests = SupportRequest.objects.filter(user=user).order_by('-created_at')
        serializer = SupportRequestSerializer(requests, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SupportRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'detail': 'Обращение отправлено'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupportRequestDetailAPIView(APIView):
    """
    API для получения одного обращения по его ID.

    GET:
    - Возвращает полную информацию об обращении с вложенными ответами администратора.
    - Только владелец обращения или администратор могут получить доступ.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, request_id):
        support_request = get_object_or_404(SupportRequest, pk=request_id)
        if not request.user.is_staff and support_request.user != request.user:
            return Response({'detail': 'Нет доступа'}, status=status.HTTP_403_FORBIDDEN)
        serializer = SupportRequestSerializer(support_request)
        return Response(serializer.data)


class SupportRequestListView(ListAPIView):
    """
    API для получения списка обращений администратором.
    """
    queryset = SupportRequest.objects.all().order_by('-created_at')
    serializer_class = SupportRequestSerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]


class SupportReplyAPIView(APIView):
    """
    API для добавления ответа администратора на обращение.

    POST:
    - Принимает сообщение ответа администратора.
    - Привязывает ответ к указанному обращению и текущему администратору.
    - Доступно только администраторам.
    """
    permission_classes = [IsAdminPermission]

    def post(self, request, request_id):
        support_request = get_object_or_404(SupportRequest, pk=request_id)
        serializer = SupportReplySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(support_request=support_request, admin=request.user)
            return Response({'detail': 'Ответ отправлен'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupportRequestStatusUpdateAPIView(APIView):
    """
    API для изменения статуса обращения администратором.

    PATCH:
    - Принимает новое значение поля `status`.
    - Проверяет корректность значения и обновляет статус обращения.
    - Доступно только администраторам.
    """
    permission_classes = [IsAdminPermission]

    def patch(self, request, request_id):
        support_request = get_object_or_404(SupportRequest, pk=request_id)
        new_status = request.data.get('status')

        if new_status not in dict(SupportRequest.STATUS_CHOICES):
            return Response({'status': 'Недопустимый статус'}, status=status.HTTP_400_BAD_REQUEST)

        support_request.status = new_status
        support_request.save()
        return Response({'detail': 'Статус обновлён'}, status=status.HTTP_200_OK)
