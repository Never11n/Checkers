from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .views import move_checker


class GameConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = 'game'
    async def connect(self):

        await self.accept()

        await self.send(text_data=json.dumps({
            'message': 'WebSocket connection established.'
        }))


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        command = data.get('command')

        if command == 'move':
            game_id = data.get('game_id')
            checker_id = data.get('checker_id')
            new_row = data.get('new_row')
            new_column = data.get('new_column')

            await self.move_checker(game_id, checker_id, new_row, new_column)

    async def move_checker(self, game_id, checker_id, new_row, new_column):
        response_data = move_checker(self.scope['user'], game_id, checker_id, new_row, new_column)

        await self.send(text_data=json.dumps(response_data))





