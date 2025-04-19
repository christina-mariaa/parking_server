from django.urls import path
from .views import ParkingStatusSummaryView, BookingStatsByTariffView, GenerateReportAPIView

urlpatterns = [
    path('parking-status/', ParkingStatusSummaryView.as_view(), name='parking-status-summary'),
    path('booking-stats/', BookingStatsByTariffView.as_view(), name='booking-stats'),
    path('reports/generate/', GenerateReportAPIView.as_view(), name='generate-report'),
]
