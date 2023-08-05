from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/game/board/<int:game_id>)', consumers.GameConsumer.as_asgi()),
]
