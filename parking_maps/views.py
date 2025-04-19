from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
import re
from api.permissions import IsAdminPermission
from parking_spots.models import ParkingSpot
from .models import ParkingMap
from .serializers import ParkingMapSerializer


def get_color_by_status(status):
    """
    Возвращает цвет в зависимости от статуса парковочного места.
    """
    colors = {
        'available': '#99CB62',
        'booked': '#F09686',
        'unavailable': '#EEEEB9'
    }
    return colors.get(status, '#FFFFFF')


def generate_svg_with_status(latest_map, parking_spots):
    """
    Генерирует SVG-файл с визуальным отображением статусов парковочных мест.

    Для каждого объекта ParkingSpot ищется SVG-элемент <rect> с соответствующим id
    (в формате 'Rectangle <spot_number>'), и изменяется его атрибут fill на цвет,
    соответствующий текущему статусу места.

    Аргументы:
        latest_map (ParkingMap): Последняя загруженная карта с SVG-файлом;
        parking_spots (QuerySet): Набор объектов ParkingSpot, содержащих информацию о статусе.

    Возвращает:
        str: Модифицированный SVG-файл в виде строки.
    """
    svg_content = latest_map.svg_file.read().decode('utf-8')

    for spot in parking_spots:
        color = get_color_by_status(spot.status)
        spot_id = f'Rectangle {spot.spot_number}'

        reg_exp = re.compile(rf'<rect[^>]*id="{spot_id}"[^>]*fill="[^"]*"', re.DOTALL)

        svg_content = re.sub(
            reg_exp,
            lambda match: match.group(0).replace(re.search(r'fill="[^"]*"', match.group(0)).group(), f'fill="{color}"'),
            svg_content
        )
    return svg_content


class LatestParkingMapView(APIView):
    """
    Представление для получения последней SVG-карты парковки с раскраской по статусу мест.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            latest_map = ParkingMap.objects.latest('uploaded_at')
        except ObjectDoesNotExist:
            return Response(
                {"error": "Карта парковки ещё не загружена."},
                status=status.HTTP_404_NOT_FOUND
            )
        parking_spots = ParkingSpot.objects.all()
        svg_with_status = generate_svg_with_status(latest_map, parking_spots)
        return Response({"svg_content": svg_with_status}, status=status.HTTP_200_OK)


class UploadParkingMapView(APIView):
    """
    Добавление карты парковки в формате SVG администратором.
    """
    permission_classes = [IsAuthenticated, IsAdminPermission]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = ParkingMapSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
