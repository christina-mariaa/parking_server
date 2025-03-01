from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from io import BytesIO

from api.reports.data_collectors import (
    collect_statistics,
    collect_bookings,
    collect_payments,
    collect_new_users,
    collect_new_cars,
)
from api.reports.report_generators import generate_xlsx_report
from api.permissions import IsAdminPermission


class GenerateReportAPIView(APIView):
    """
    Генерация отчетов администратором.
    """
    permission_classes = [IsAuthenticated, IsAdminPermission]

    def post(self, request):
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        include = request.data.get('include', [])  # ["statistics", "bookings", ...]

        if not start_date or not end_date:
            return Response({"error": "start_date and end_date are required"}, status=400)

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

        file_data = generate_xlsx_report(data)
        file_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        response = HttpResponse(file_data.getvalue(), content_type=file_type)
        response['Content-Disposition'] = f'attachment; filename="report.xlsx"'
        return response
