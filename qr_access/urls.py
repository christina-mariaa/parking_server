from django.urls import path
from .views import QRView, VerifyQRCodeAccessView, QRAccessLogListView


urlpatterns = [
    path('qrcode/generate/<booking_id>/', QRView.as_view(), name='generate-qrcode'),
    path('qrcode/verify-access/', VerifyQRCodeAccessView.as_view(), name='verify-access'),
    path('qrcode/logs/', QRAccessLogListView.as_view(), name='access-logs')
]
