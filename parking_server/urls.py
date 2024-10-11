from django.urls import path
from api.views import UserRegistrationView, ConfirmEmailView, AddCarView
from django.contrib import admin
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('confirm-email/<uidb64>/<token>/', ConfirmEmailView.as_view(), name='confirm-email'),
    path('add-car/', AddCarView.as_view(), name='add-car'),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # получение токена
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # обновление токена
]
