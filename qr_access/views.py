from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .qr_generator import generate_qr_code
from bookings.models import Booking


class QRView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, car__user=request.user)
        except Booking.DoesNotExist:
            return Response({"error: Бронирование не найдено"}, status=status.HTTP_404_NOT_FOUND)

        start_time = booking.start_time
        end_time = booking.end_time
        qr = generate_qr_code(booking_id, start_time, end_time)

        return Response(qr, status=status.HTTP_200_OK)
