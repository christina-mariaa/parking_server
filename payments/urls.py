from django.urls import path
from .views import UserPaymentListView, UserMakePaymentView, AdminPaymentListView


urlpatterns = [
    path('user/', UserPaymentListView.as_view(), name='user-payments'),
    path('user/<int:booking_id>/', UserMakePaymentView.as_view(), name='create-payment'),
    path('admin/', AdminPaymentListView.as_view(), name='admin-payments'),
]
