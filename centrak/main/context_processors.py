from datetime import date
from django.conf import settings

from . import utils



def menu(request):
    """Adds the application menu to the context."""
    return {'menu': lambda: utils.Menu(request)}


def current_date(request):
    """Adds the current date to the context."""
    return {'current_date': lambda: date.today() }


def jsconf(request):
    """Provides some JavaScript configuration."""
    return {
        'api_root': settings.CENTRAK_API_ROOT,
        'survey_api_root': settings.SURVEY_API_ROOT,
        'survey_auth_api_root': settings.SURVEY_AUTH_API_ROOT,
    }
