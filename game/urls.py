from django.urls import path
from . import views
from . import consumers
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('board/<int:game_id>/', views.board_view, name='board_print'),
    path('move_checker/<int:checker_id>/<int:new_row>/<int:new_column>/', consumers.GameConsumer, name='move_checker'),
    path('invite/', csrf_exempt(views.invite_to_game), name='invite_to_game'),
]
