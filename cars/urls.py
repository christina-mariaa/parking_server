from django.urls import path
from .views import UserCarListCreateView, UserCarDeleteView, AdminCarListView


urlpatterns = [
    path('user/', UserCarListCreateView.as_view(), name='cars-user-list-create'),
    path('user/<int:car_id>/', UserCarDeleteView.as_view(), name='cars-user-delete'),
    path('admin/', AdminCarListView.as_view(), name='cars-list')
]
