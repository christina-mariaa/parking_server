from django.urls import path
from .views import ParkingSpotListCreateView, ParkingSpotUpdateDeleteView, BulkCreateParkingSpotsView


urlpatterns = [
    path('', ParkingSpotListCreateView.as_view(), name='parking-spot-list-create'),
    path('admin/bulk-create/', BulkCreateParkingSpotsView.as_view(), name='bulk-create-parking-spots'),
    path('admin/<str:spot_number>/', ParkingSpotUpdateDeleteView.as_view(), name='parking-spot-detail'),
]
