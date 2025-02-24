import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import parking_server.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parking_server.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            parking_server.routing.websocket_urlpatterns  # Маршруты WebSocket
        )
    ),
})