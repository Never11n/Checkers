# Generated by Django 4.2.3 on 2023-07-24 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_checkers_current_turn'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkers',
            name='captured',
            field=models.BooleanField(default=False),
        ),
    ]
