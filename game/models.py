from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    white_player = models.ForeignKey(User, related_name="white_games", on_delete=models.CASCADE)
    black_player = models.ForeignKey(User, related_name="black_games", on_delete=models.CASCADE)
    white_score = models.IntegerField(default=0)
    black_score = models.IntegerField(default=0)
    current_turn = models.CharField(max_length=5, choices=[('white', 'White'), ('black', 'Black')], default='white')
    game_over = models.BooleanField(default=False)


class Checkers(models.Model):
    id = models.AutoField(primary_key=True)
    color = models.CharField(max_length=10)
    row = models.IntegerField()
    column = models.IntegerField()
    current_turn = models.CharField(max_length=5, default='white', choices=(('white', 'White'), ('black', 'Black')))
    captured = models.BooleanField(default=False)
    on_board = models.BooleanField(default=True)
    game = models.ForeignKey(Game, related_name="checkers", on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ('row', 'column', 'captured')

