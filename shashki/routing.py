from channels.routing import ProtocolTypeRouter, URLRouter
import game.routing
from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': URLRouter(
        game.routing.websocket_urlpatterns
    ),
})
