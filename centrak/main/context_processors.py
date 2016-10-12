from datetime import date
from django.conf import settings


def current_date(request):
    """Adds the current date to the context."""
    return {'current_date': lambda: date.today() }
