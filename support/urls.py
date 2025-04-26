from django.urls import path
from .views import (
    SupportRequestListCreateAPIView,
    SupportRequestDetailAPIView,
    SupportRequestListView,
    SupportReplyAPIView,
    SupportRequestStatusUpdateAPIView,
)

urlpatterns = [
    path('user/', SupportRequestListCreateAPIView.as_view(), name='support-list-create'),
    path('user/<int:request_id>/', SupportRequestDetailAPIView.as_view(), name='support-detail'),
    path('admin/requests/', SupportRequestListView.as_view(), name='support-requests'),
    path('admin/<int:request_id>/reply/', SupportReplyAPIView.as_view(), name='support-reply'),
    path('admin/<int:request_id>/status/', SupportRequestStatusUpdateAPIView.as_view(), name='support-status'),
]
