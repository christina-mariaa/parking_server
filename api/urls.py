from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (UserRegistrationView,
                    CustomTokenObtainPairView,
                    UserProfileView,
                    AdminUserViewSet,
                    UpdateAdminStatusView)
from rest_framework_simplejwt.views import TokenRefreshView


router = DefaultRouter()
router.register(r'', AdminUserViewSet, basename='admin-user')

urlpatterns = [
    path('', UserProfileView.as_view(), name='user-profile'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/', include(router.urls)),
    path('admin/<int:user_id>/update-admin-status/', UpdateAdminStatusView.as_view(), name='update-admin-status'),
]
