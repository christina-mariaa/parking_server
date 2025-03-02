from django.urls import path, include
from api.views import *
from django.contrib import admin
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

admin_patterns = [
    path('users/', AdminUserViewSet.as_view({'get': 'list'}), name='admin-users'),
    path('users/<int:pk>/', AdminUserViewSet.as_view({'get': 'retrieve'}), name='admin-user-detail'),
    path('bookings/', AdminBookingViewSet.as_view({'get': 'list'}), name='admin-bookings'),
    path('payments/', AdminPaymentViewSet.as_view({'get': 'list'}), name='admin-payments'),
    path('cars/', AdminCarViewSet.as_view({'get': 'list'}), name='admin-cars'),
    path('users/<int:user_id>/update-admin-status/', UpdateAdminStatusView.as_view(), name='update-admin-status'),
    path('tariffs/', TariffView.as_view(), name='admin-tariff-list-create'), # Для GET
    path('tariffs/<int:tariff_id>/', TariffView.as_view(), name='admin-tariff-update'), # Для PATCH

    path('parking-spots/', ParkingSpotView.as_view(), name='parking-spot-list-create'), # Для списка парковочных мест (GET) и создания (POST)
    path('parking-spots/bulk-create/', BulkCreateParkingSpotsView.as_view(), name='bulk-create-parking-spots'), # Для массового добавления парковочных мест
    path('parking-spots/<str:spot_number>/', ParkingSpotView.as_view(), name='parking-spot-detail'), # Для обновления (PATCH) и удаления (DELETE) конкретного места
    path('upload-parking-map/', UploadParkingMapView.as_view(), name='upload_parking_map'),
    path('parking-status/', ParkingStatusSummaryView.as_view(), name='parking_status_summary'),
    path('booking-stats/', BookingStatsByTariffView.as_view(), name='booking-stats'),

    path('reports/', include('api.reports.urls')),
]

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # обновление токена
    path('admin/', admin.site.urls),

    path('user/cars/', UserCarView.as_view(), name='user-cars'),  # Для GET и POST
    path('user/cars/<int:car_id>/', UserCarView.as_view(), name='delete-car'),  # Для DELETE

    path('user/bookings/', UserBookingView.as_view(), name='user-bookings'),

    path('user/payments/', UserPaymentView.as_view(), name='user-payments'),  # Для GET
    path('user/payments/<int:booking_id>/', UserPaymentView.as_view(), name='create-payment'),  # Для POST с указанием бронирования

    path('parking-map/latest/', LatestParkingMapView.as_view(), name='latest_parking_map'),
    path('tariffs/', TariffsListView.as_view(), name='tariffs_list'),

    path('api/admin/', include((admin_patterns, 'admin'), namespace='admin')),
    path('qrcode/', include('api.qr_access.urls')),
]
