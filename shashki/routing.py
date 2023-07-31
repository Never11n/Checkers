from channels.routing import ProtocolTypeRouter, URLRouter
from game import routing as game_routing
from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': URLRouter(
        game_routing.websocket_urlpatterns
    ),
})
