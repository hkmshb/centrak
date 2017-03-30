from datetime import date
from django.conf import settings
from core.models import Notification
from . import utils


def current_date(request):
    """Adds the current date to the context.
    """
    return {'current_date': lambda: date.today() }


def jsconf(request):
    """Provides some JavaScript configuration.
    """
    context = {'api_root': settings.CENTRAK_API_ROOT}
    if utils.is_admin_view(request):
        context.update({
        })
    return context


def menu(request):
    """Adds the application menu to the context.
    """
    return {'menu': lambda: utils.Menu(request)}


def notification_count(request):
    """Adds long lived notifications for current user to the context.
    """
    user_id = request.user.id
    if not user_id:
        return {'notifications': 0}
    
    count = Notification.objects.filter(user_id=user_id, read=False).count()
    return {'notification_count': count}

