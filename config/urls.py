from django.urls import path, include
from django.contrib import admin
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Parking API",
      default_version='v1',
      description="Документация API автостоянки",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('users/', include('api.urls')),
    path('cars/', include('cars.urls')),
    path('tariffs/', include('tariffs.urls')),
    path('bookings/', include('bookings.urls')),
    path('payments/', include('payments.urls')),
    path('parking-spots/', include('parking_spots.urls')),
    path('parking-maps/', include('parking_maps.urls')),
    path('access/', include('qr_access.urls')),
    path('analytics/admin/', include('analytics.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('admin/', admin.site.urls),
]
