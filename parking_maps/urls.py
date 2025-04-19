from django.urls import path
from .views import LatestParkingMapView, UploadParkingMapView


urlpatterns = [
    path('latest/', LatestParkingMapView.as_view(), name='latest-parking-map'),
    path('admin/upload/', UploadParkingMapView.as_view(), name='upload-parking-map'),
]
