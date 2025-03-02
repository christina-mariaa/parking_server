from django.urls import path
from .views import QRView

urlpatterns = [
    path('generate/<booking_id>/', QRView.as_view(), name='generate-qrcode')
]
