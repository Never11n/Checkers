from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.sessions.models import Session
from .forms import SignUpForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from game.models import Game

# Create your views here.


def mainpage(request):
    return render(request, 'main/mainpage.html')


def login(request):
    if request.user.is_authenticated:
        request.session['user_id'] = request.user.id
        request.session['is_online'] = True
        return render(request, 'registration/login.html')


def logout(request):
    auth_logout(request)
    request.session.pop('user_id', None)
    request.session.pop('is_online', None)
    return redirect('main')


def signup(request):
    form = SignUpForm(request.POST)
    if request.method == "POST":

        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('login')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'forms': form})


def player_info(request):
    now = timezone.now()
    sessions = Session.objects.filter(expire_date__gte=now)
    players = User.objects.all()
    online_users = []
    for session in sessions:
        user_id = session.get_decoded().get('_auth_user_id')
        for player in players:
            if str(player.id) == user_id:
                online_users.append(player)
    context = {'players': online_users}
    return render(request, 'main/mainpage.html', context)


@csrf_exempt
def create_game(request):
    if request.method == "POST":
        game = Game.objects.create()
        return JsonResponse({'message': 'Игра создана', 'game_id': game.id}, status=201)
    else:
        return JsonResponse({'error': 'Неверный HTTP метод'}, status=400)
