from django.shortcuts import render, reverse
from .models import Checkers, Game
from django.contrib.auth.models import User
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


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
