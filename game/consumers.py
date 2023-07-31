from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import Checkers
from channels.db import database_sync_to_async


class GameConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = None
        self.room_group_name = None

    @database_sync_to_async
    def move_checker_to_position(self, checker, new_row, new_column):
        checker.row = new_row
        checker.column = new_column
        checker.save()

    async def is_valid_move(self, checker, new_row, new_column):
        if checker.captured:
            return False

        if not (1 <= new_row <= 8) or not (1 <= new_column <= 8):
            return False

        direction = 1 if checker.color == 'white' else -1
        if abs(new_column - checker.column) == 1 and new_row - checker.row == direction:
            return True

        return False

    @database_sync_to_async
    def remove_checker(self, checker):
        checker.captured = True
        checker.save()

    async def can_continue_attack(self, checker, attacking_color):
        directions = [(2, 2), (-2, 2), (-2, -2), (2, -2)]

        for direct in directions:
            target_row, target_column = checker.row + direct[0], checker.column + direct[1]
            captured_row, captured_column = checker.row + direct[0] // 2, checker.column + direct[1] // 2

            if await self.is_valid_attack(checker.row, checker.column, target_row, target_column, captured_row,
                                          captured_column, attacking_color):
                behind_checker = await self.get_checker(target_row, target_column)
                if not behind_checker:
                    return True

        return False

    @database_sync_to_async
    def get_checker(self, row, column, checker):
        return Checkers.objects.filter(row=row, column=column, attacking_color=checker.color).first()

    async def is_valid_attack(self, start_row, start_column, target_row, target_column, captured_row, captured_column,
                              attacking_color):
        if not (0 <= target_row < 8 and 0 <= target_column < 8):
            return False
        row_diff = abs(start_row - target_row)
        column_diff = abs(start_column - target_column)
        if row_diff == 2 and column_diff == 2:
            captured_checker = await self.get_checker(captured_row, captured_column)
            if captured_checker and captured_checker.color != attacking_color and not captured_checker.captured:
                print(
                    f"Valid attack: Captured checker at ({captured_row},{captured_column})"
                    f" with color {captured_checker.color}")
                target_checker = await self.get_checker(target_row, target_column)
                if not target_checker:
                    return True

        return False

    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = 'checkers_%s' % self.game_id

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        command = data.get('command')

        if command == 'move':
            await self.move_checker(data)

    @database_sync_to_async
    def get_checker_by_id(self, checker_id):
        return Checkers.objects.get(pk=checker_id)

    @database_sync_to_async
    def get_captured_checkers(self):
        captured_checkers = Checkers.objects.filter(captured=True)
        return [checker.id for checker in captured_checkers]

    @database_sync_to_async
    def opposite_color(self, color):
        return 'black' if color == 'white' else 'white'

    async def move_checker(self, data):
        checker_id = data['checker_id']
        new_row = int(data['new_row'])
        new_column = int(data['new_column'])

        checker = await self.get_checker_by_id(checker_id)
        game = checker.game
        current_turn = game.current_turn

        if checker.color != current_turn:
            await self.send(text_data=json.dumps({'error': 'Сейчас не ваш ход'}))
            return

        captured_row = (checker.row + new_row) // 2
        captured_column = (checker.column + new_column) // 2

        if await self.is_valid_attack(int(checker.row), int(checker.column), int(new_row), int(new_column),
                                      captured_row, captured_column, checker.color):
            print("Valid attack detected!")
            target_enemy_checker = await self.get_checker(captured_row,
                                                          captured_column,
                                                          self.opposite_color(checker.color))
            if target_enemy_checker and not target_enemy_checker.captured:
                target_enemy_checker.captured = True
                captured_checkers = [target_enemy_checker.id]
                await database_sync_to_async(target_enemy_checker.save)()

                await self.move_checker_to_position(checker, new_row, new_column)
                can_continue = await self.can_continue_attack(checker, checker.color)

                response_data = {
                    'message': 'Успешная атака',
                    'capture': True,
                    'attacking_checker': {'id': checker.id, 'color': checker.color},
                    'captured_checkers': captured_checkers,
                    'can_continue_attack': can_continue,
                }

                try:
                    if not can_continue:
                        game.current_turn = 'black' if current_turn == 'white' else 'white'
                        await database_sync_to_async(game.save)()
                        await database_sync_to_async(target_enemy_checker.delete)()
                    else:
                        game.attacking_checker_id = checker.id
                        await database_sync_to_async(game.save)()
                except Exception as e:
                    print(f'Error deleting checker: {str(e)}')

                await self.send(text_data=json.dumps(response_data))

                return

        if await self.is_valid_move(checker, new_row, new_column):
            print("Valid move detected!")
            target_checker = await self.get_checker(new_row, new_column)

            if not target_checker:
                await self.move_checker_to_position(checker, new_row, new_column)

                game.current_turn = 'black' if current_turn == 'white' else 'white'
                await database_sync_to_async(game.save)()

                await self.send(text_data=json.dumps({'message': 'Успешный ход'}))
                return

        await self.send(text_data=json.dumps({'error': 'Неверный ход'}))








