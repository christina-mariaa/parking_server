from django.urls import path
from .views import GenerateReportAPIView

urlpatterns = [
    path('generate/', GenerateReportAPIView.as_view(), name='generate-report'),
]
