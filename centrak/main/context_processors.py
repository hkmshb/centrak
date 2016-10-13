from datetime import date
from django.conf import settings
from . import utils


def current_date(request):
    """Adds the current date to the context."""
    return {'current_date': lambda: date.today() }


def menu(request):
    """Adds the application menu to the context."""
    return {'menu': lambda: utils.Menu(request)}
