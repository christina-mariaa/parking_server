from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/parking_map/$', consumers.ParkingMapConsumer.as_asgi()),
    re_path(r'ws/admin/users$', consumers.AdminUserConsumer.as_asgi()),
    re_path(r'ws/admin/cars$', consumers.AdminCarConsumer.as_asgi()),
    re_path(r'ws/admin/bookings$', consumers.AdminBookingConsumer.as_asgi()),
    re_path(r'ws/admin/payments$', consumers.AdminPaymentConsumer.as_asgi()),
]