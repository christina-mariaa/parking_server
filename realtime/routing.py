from django.urls import re_path
from .consumers.users import AdminUserConsumer
from .consumers.cars import AdminCarConsumer
from .consumers.bookings import AdminBookingConsumer
from .consumers.payments import AdminPaymentConsumer
from .consumers.parking_spots import ParkingSpotConsumer


websocket_urlpatterns = [
    re_path(r'ws/parking_spots$', ParkingSpotConsumer.as_asgi()),
    re_path(r'ws/admin/users$', AdminUserConsumer.as_asgi()),
    re_path(r'ws/admin/cars$', AdminCarConsumer.as_asgi()),
    re_path(r'ws/admin/bookings$', AdminBookingConsumer.as_asgi()),
    re_path(r'ws/admin/payments$', AdminPaymentConsumer.as_asgi()),
]
