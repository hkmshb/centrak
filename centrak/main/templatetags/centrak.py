from urllib.parse import urlencode

from django.core.urlresolvers import reverse
from django.conf import settings
from django import template


register = template.Library()



@register.filter
def can_change_region(user):
    if user.is_superuser:
        return True
    return False


@register.filter
def equal(value, expected):
    return value == expected


@register.filter
def fa_synced_by(synced_by, default):
    if synced_by not in ('', None):
        return 'fa-laptop' if synced_by == 'auto' else 'fa-user'
    return 'fa-question'


@register.filter
def fa_notification_read(read):
    return 'fa-envelope-open-o' if read else 'fa-envelope'


@register.filter
def replace(s, args):
    parts = args.split(',')
    if len(parts) != 2:
        raise ValueError("replace args format: 'old,new'")
    return s.replace(parts[0], parts[1])


@register.filter
def split(s, sep=','):
    if s and sep in s:
        return s.split(sep)
    return s


@register.filter
def user_fullname(user):
    value = user.last_name
    if user.first_name:
        if value:
            value += ", "
        value += user.first_name
    return value


@register.filter
def user_roles(user):
    value = ""
    if user.groups.exists:
        value = ", ".join([g.name for g in user.groups.all()])
    return value


@register.filter
def update_qs(request, page):
    qs = request.GET.copy()
    qs.update({ settings.CENTRAK_QS_PARAM_PAGE: page })
    return urlencode(qs)


@register.filter
def urlcancel(form, default_url):
    if form.instance:
        if form.url_cancel:
            return form.url_cancel
        elif form.instance._get_pk_val():
            return form.instance.get_absolute_url()
    
    if (default_url.startswith('@')):
        return reverse(default_url.replace('@',''))
    return default_url

