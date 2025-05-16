from django.http import HttpResponse
from django.db import models
from django.db.models import Count, Case, When
from django.utils.timezone import now, timedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from api.permissions import IsAdminPermission
from parking_spots.models import ParkingSpot
from bookings.models import Booking
from analytics.report_generators import generate_xlsx_report
from analytics.data_collectors import (
    collect_statistics,
    collect_bookings,
    collect_payments,
    collect_new_users,
    collect_new_cars,
)


class ParkingStatusSummaryView(APIView):
    """
    Получение статистики по статусам мест администратором.
    """
    permission_classes = [IsAuthenticated, IsAdminPermission]

    def get(self, request):
        status_counts = ParkingSpot.objects.values('status').annotate(count=Count('status'))
        result = {item['status']: item['count'] for item in status_counts}
        return Response(result)


class BookingStatsByTariffView(APIView):
    """
    Получение статистики по бронированиям за день, неделю, месяц администратором.
    """
    permission_classes = [IsAuthenticated, IsAdminPermission]

    def get(self, request):
        # Текущее время
        today = now()

        # Периоды для статистики
        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_week = start_of_day - timedelta(days=start_of_day.weekday())  # Понедельник текущей недели
        start_of_month = start_of_day.replace(day=1)  # Первое число текущего месяца
        start_of_year = today.replace(month=1, day=1)  # Первое января текущего года

        periods = {
            "day": start_of_day,
            "week": start_of_week,
            "month": start_of_month,
            "year": start_of_year,
        }

        # Словарь для хранения данных статистики
        stats = {}
        for period_name, start_time in periods.items():
            data = (
                Booking.objects.filter(start_time__gte=start_time)
                .values("tariff__name")
                .annotate(
                    count=Count("id"),  # Общее количество бронирований
                    unpaid_count=Count(  # Количество неоплаченных бронирований
                        Case(
                            When(payment__isnull=True, then=1),  # Условие: если оплаты нет
                            output_field=models.IntegerField(),
                        )
                    ),
                )
            )
            stats[period_name] = list(data)

        return Response(stats)


class GenerateReportAPIView(APIView):
    """
    Генерация отчетов администратором.
    """
    permission_classes = [IsAuthenticated, IsAdminPermission]

    def post(self, request):
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        include = request.data.get('include', [])  # ["statistics", "bookings", ...]

        if not start_date or not end_date or not include:
            return Response({"error": "start_date, end_date and include are required"}, status=400)

        if not isinstance(include, list) or not include:
            return Response({"error": "Поле 'include' должно быть списком содержать хотя бы один элемент"}, status=400)

        data = {}
        if 'statistics' in include:
            data['statistics'] = collect_statistics(start_date, end_date)
        if 'bookings' in include:
            data['bookings'] = collect_bookings(start_date, end_date)
        if 'payments' in include:
            data['payments'] = collect_payments(start_date, end_date)
        if 'new_users' in include:
            data['new_users'] = collect_new_users(start_date, end_date)
        if 'new_cars' in include:
            data['new_cars'] = collect_new_cars(start_date, end_date)

        if not data:
            return Response({"error": "В 'include' должны быть только допустимые значения"}, status=400)

        file_data = generate_xlsx_report(data)
        file_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        response = HttpResponse(file_data.getvalue(), content_type=file_type)
        response['Content-Disposition'] = f'attachment; filename="report.xlsx"'
        return response
