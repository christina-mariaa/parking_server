from django.urls import path
from .views import TariffsListView, TariffView, TariffUpdateView

urlpatterns = [
    path('user/', TariffsListView.as_view(), name='tariff-list'),
    path('admin/', TariffView.as_view(), name='admin-tariff-list-create'),
    path('admin/<int:tariff_id>/', TariffUpdateView.as_view(), name='admin-tariff-update'),
]
