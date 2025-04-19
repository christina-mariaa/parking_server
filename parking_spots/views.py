from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from api.permissions import IsAdminPermission
from rest_framework.response import Response
from rest_framework import status
from .models import ParkingSpot
from .serializers import ParkingSpotSerializer, UpdateSpotSerializer
from bookings.models import Booking


class ParkingSpotListCreateView(APIView):
    """
    Представление для получения списка и создания парковочных мест.

    Поддерживает:
        - GET: получение списка всех парковочных мест (доступно авторизованным пользователям).
        - POST: создание нового парковочного места (только для администратора).
    """

    def get_permissions(self):
        """
        Для GET — достаточно быть авторизованным пользователем.
        Для POST — требуется быть администратором.
        """
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminPermission()]

    def get(self, request):
        """
        Возвращает отсортированный список всех парковочных мест.
        """
        parking_spots = ParkingSpot.objects.all().order_by('spot_number')
        serializer = ParkingSpotSerializer(parking_spots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Создание нового парковочного места.

        Ограничения:
            - Номер места обязателен.
            - Статус: 'available' или 'unavailable'.
            - Место с таким номером не должно существовать.
        """
        spot_number = request.data.get("spot_number")
        status_value = request.data.get("status")

        if not spot_number:
            return Response({"error": "Номер места обязателен."}, status=400)

        if status_value and status_value not in ["available", "unavailable"]:
            return Response({"error": "Неверный статус. Допустимы только 'available' или 'unavailable'."}, status=400)

        if ParkingSpot.objects.filter(spot_number=spot_number).exists():
            return Response({"error": f"Место с номером {spot_number} уже существует."}, status=400)

        spot = ParkingSpot.objects.create(spot_number=spot_number, status=status_value)
        return Response(ParkingSpotSerializer(spot).data, status=201)


class ParkingSpotUpdateDeleteView(APIView):
    """
    Представление для обновления и удаления одного парковочного места.

    Поддерживает:
        - PATCH: обновление статуса парковочного места.
        - DELETE: удаление парковочного места.

    Только для администратора.
    """
    permission_classes = [IsAuthenticated, IsAdminPermission]

    def patch(self, request, spot_number):
        """
        Обновление статуса парковочного места.

        Ограничения:
            - Указывается только статус.
            - Место должно существовать.
        """
        try:
            spot = ParkingSpot.objects.get(spot_number=spot_number)
        except ParkingSpot.DoesNotExist:
            return Response({"error": "Место не найдено"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateSpotSerializer(spot, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Статус места успешно обновлен",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, spot_number):
        """
        Удаление парковочного места.

        Ограничения:
            - Место не должно быть связано с активным бронированием.
            - Место должно существовать.
        """
        try:
            spot = ParkingSpot.objects.get(spot_number=spot_number)

            if Booking.objects.filter(parking_place=spot, status='active').exists():
                return Response({
                    "error": f"Место {spot_number} не может быть удалено, так как оно забронировано."
                }, status=400)

            spot.delete()
            return Response({
                "detail": f"Парковочное место {spot_number} успешно удалено."
            }, status=200)

        except ParkingSpot.DoesNotExist:
            return Response({"error": f"Парковочное место {spot_number} не найдено."}, status=404)


class BulkCreateParkingSpotsView(APIView):
    """
    Представление для массового добавления парковочных мест администратором.

    Ограничения и проверки:
        - Запрос должен содержать список объектов.
        - Каждый объект должен содержать уникальный `spot_number`.
        - Допустимые значения `status`: 'available', 'unavailable'.
        - Если `spot_number` уже существует в базе — место не создаётся и добавляется в список ошибок.
    """
    permission_classes = [IsAuthenticated, IsAdminPermission]

    def post(self, request):
        # Проверка, что запрос содержит список объектов
        if not isinstance(request.data, list):
            return Response({"error": "Ожидался список объектов для добавления."}, status=404)

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
