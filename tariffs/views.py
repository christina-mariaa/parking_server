from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.permissions import IsAdminPermission
from .models import Tariff, TariffPriceHistory
from .serializers import TariffSerializer, AdminTariffSerializer, UpdateTariffSerializer, TariffPriceHistorySerializer


class TariffsListView(ListAPIView):
    """
    Представление для получения списка всех доступных тарифов.

    Только для чтения. Доступно авторизованным пользователям.
    """
    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer
    permission_classes = [IsAuthenticated]


class TariffView(APIView):
    """
    Представление для управления тарифами администратором.

    Методы:
    - GET: получить список всех тарифов
    - POST: создать новый тариф
    """
    permission_classes = [IsAuthenticated, IsAdminPermission]

    def get(self, request):
        """
        Получение списка всех тарифов.
        """
        tariffs = Tariff.objects.all().order_by('id')
        serializer = AdminTariffSerializer(tariffs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Создание нового тарифа.
        """
        serializer = AdminTariffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TariffUpdateView(APIView):
    """
    Представление для обновления стоимости тарифа администратором.
    """
    permission_classes = [IsAuthenticated, IsAdminPermission]

    def patch(self, request, tariff_id):
        """
        Обновление цены тарифа по ID.
        """
        try:
            tariff = Tariff.objects.get(id=tariff_id)
        except Tariff.DoesNotExist:
            return Response({"error": "Тариф не найден"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateTariffSerializer(tariff, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Тариф успешно обновлен", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TariffPriceHistoryListView(ListAPIView):
    """
    Представление для получения истории обновления цен тарифов.
    """
    queryset = TariffPriceHistory.objects.all()
    serializer_class = TariffPriceHistorySerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]
