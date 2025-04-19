from django.urls import path
from .views import UserBookingView, AdminBookingListView

urlpatterns = [
    path('user/', UserBookingView.as_view(), name='user-bookings'),  # GET — список, POST — создать бронирование
    path('admin/', AdminBookingListView.as_view(), name='admin-bookings'),  # GET — список всех бронирований
]
