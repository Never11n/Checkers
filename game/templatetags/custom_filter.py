from django import template
from game.models import Checkers

register = template.Library()


@register.filter
def get_checker_id(row, col):
    try:
        checker = Checkers.objects.filter(row=row, column=col).first()
        return checker.id
    except Checkers.DoesNotExist:
        print(f"Checker not found at row={row}, col={col}")
        return None
