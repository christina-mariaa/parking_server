from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from api.permissions import IsAdminPermission
from bookings.models import Booking
from .models import Payment
from .serializers import PaymentSerializer, AdminPaymentListSerializer


class UserPaymentListView(ListAPIView):
    """
    Представление возвращает список всех оплат, сделанных текущим пользователем.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(booking__car__user=self.request.user)


class UserMakePaymentView(APIView):
    """
    Создаёт новую оплату по указанному ID бронирования (передаётся в URL).
    Доступно только если бронирование принадлежит текущему пользователю.
    Сумма оплаты определяется автоматически в модели Payment на основе цены тарифа, связанного с бронированием.
    """
    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Бронирование не найдено."}, status=status.HTTP_404_NOT_FOUND)

        if booking.status != "active":
            return Response({"error": "Бронирование уже неактивно."}, status=status.HTTP_400_BAD_REQUEST)

        if booking.car.user != request.user:
            return Response({"error": "Вы не можете оплатить чужое бронирование."}, status=status.HTTP_403_FORBIDDEN)

        serializer = PaymentSerializer(data={'booking': booking.id})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminPaymentPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdminPaymentListView(ListAPIView):
    """
    Представление для получения списка всех оплат администратором.
    """
    queryset = Payment.objects.select_related('booking__car__user', 'booking__tariff').order_by('-id')
    serializer_class = AdminPaymentListSerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]
    pagination_class = AdminPaymentPagination
