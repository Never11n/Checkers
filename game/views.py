from django.shortcuts import render
from .models import Checkers, Game
from django.contrib.auth.models import User
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


@csrf_exempt
def invite_to_game(request):
    if request.method == 'POST':

        print('Invite to game received POST request')
        print(request.body)
        player_id = json.loads(request.body).get('player_id')
        print('Player ID: ', player_id)
        player = User.objects.get(id=player_id)
        print('Player: ', player)

        try:
            game = Game.objects.create(white_player=request.user, black_player=player)
            print(game)
        except Exception as e:
            print(f"Failed to create new game: {e}")
            return JsonResponse({'error': 'Failed to create new game.'}, status=400)

        game.save()
        board_print(request, game.id)
        return JsonResponse({'game_id': game.id})
    else:
        print('Invite to game did not receive POST request')
        return JsonResponse({'error': 'Invalid request method'})


def move_checker(request, game_id, checker_id, new_row, new_column):
    game = get_object_or_404(Game, id=game_id)
    checker = get_object_or_404(Checkers, id=checker_id)

    if game.current_turn != checker.color:
        return JsonResponse({'error': 'Сейчас не ваш ход.'}, status=400)

    captured_row = (checker.row + new_row) // 2
    captured_column = (checker.column + new_column) // 2

    if is_valid_attack(checker.row, checker.column, new_row, new_column, captured_row, captured_column, checker.color):
        target_enemy_checker = Checkers.objects.filter(row=captured_row, column=captured_column, color=opposite_color(checker.color)).first()
        if target_enemy_checker and not target_enemy_checker.captured:
            target_enemy_checker.captured = True
            target_enemy_checker.save()

            move_checker_to_position(checker, new_row, new_column)
            can_continue = can_continue_attack(checker, checker.color)

            response_data = {
                'message': 'Успешная атака',
                'capture': True,
                'attacking_checker': {'id': checker.id, 'color': checker.color},
                'captured_checkers': [target_enemy_checker.id],
                'can_continue_attack': can_continue,
            }

            if not can_continue:
                game.current_turn = 'black' if game.current_turn == 'white' else 'white'
                game.save()
                target_enemy_checker.delete()
            else:
                game.attacking_checker_id = checker.id
                game.save()

            return JsonResponse(response_data)

    if is_valid_move(checker, new_row, new_column):
        target_checker = Checkers.objects.filter(row=new_row, column=new_column).first()

        if not target_checker:
            move_checker_to_position(checker, new_row, new_column)

            game.current_turn = 'black' if game.current_turn == 'white' else 'white'
            game.save()

            return JsonResponse({'message': 'Успешный ход'})

    return JsonResponse({'error': 'Неверный ход.'}, status=400)


def is_valid_attack(start_row, start_column, target_row, target_column, captured_row, captured_column, attacking_color):
    if not (0 <= target_row < 8 and 0 <= target_column < 8):
        return False

    row_diff = abs(start_row - target_row)
    column_diff = abs(start_column - target_column)

    if row_diff == 2 and column_diff == 2:
        captured_checker = Checkers.objects.filter(row=captured_row, column=captured_column).first()
        if captured_checker and captured_checker.color != attacking_color and not captured_checker.captured:
            return True

    return False

def is_valid_move(checker, new_row, new_column):
    if checker.captured:
        return False

    if not (1 <= new_row <= 8) or not (1 <= new_column <= 8):
        return False

    direction = 1 if checker.color == 'white' else -1
    if abs(new_column - checker.column) == 1 and new_row - checker.row == direction:
        return True

    return False

def move_checker_to_position(checker, new_row, new_column):
    checker.row = new_row
    checker.column = new_column
    checker.save()

def can_continue_attack(checker, attacking_color):
    directions = [(2, 2), (-2, 2), (-2, -2), (2, -2)]

    for direct in directions:
        target_row, target_column = checker.row + direct[0], checker.column + direct[1]
        captured_row, captured_column = checker.row + direct[0] // 2, checker.column + direct[1] // 2

        if is_valid_attack(checker.row, checker.column, target_row, target_column, captured_row, captured_column, attacking_color):
            behind_checker = Checkers.objects.filter(row=target_row, column=target_column).first()
            if not behind_checker:
                return True

    return False

def opposite_color(color):
    return 'black' if color == 'white' else 'white'


def board_print(request, game_id):
    Checkers.objects.all().delete()
    game = Game.objects.get(id=game_id)
    checkers_rows = [0, 1, 2, 5, 6, 7]
    board = []
    for row in range(8):
        temp = []
        for col in range(8):
            cell_info = {'color': 'white' if (row + col) % 2 == 0 else 'black', 'checker': None}
            if row in checkers_rows and (row + col) % 2 != 0:
                try:
                    checker = Checkers.objects.get(game=game, color='white' if row < 3 else 'black', row=row, column=col)
                    cell_info['checker'] = '●' if row < 3 else '○'
                    cell_info['checker_id'] = checker.id
                except Checkers.DoesNotExist:
                    checker = Checkers.objects.create(
                        game=game,
                        color='white' if row < 3 else 'black',
                        row=row,
                        column=col,
                    )
                    cell_info['checker'] = '●' if row < 3 else '○'
                    cell_info['checker_id'] = checker.id

            temp.append(cell_info)
        board.append(temp)

    return board


def board_view(request, game_id):
    board_data = board_print(request, game_id)
    return render(request, 'game/board.html', {"board_data": board_data})
