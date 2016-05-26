from django.contrib.humanize.templatetags import humanize
from . import register


@register.filter
def as_fa_user_or_pc(synced_by):
    if synced_by:
        return "user" if synced_by != "auto" else "laptop"
    return "question"


@register.filter
def momentize(dt):
    if dt:
        value = humanize.naturalday(dt)
        if value == "today":
            return dt.strftime('%H:%M')
        return value
    return "unknown"
