from core.utils import tag_registerer as register
from django.utils import safestring



@register.filter
def as_fa_user_or_pc(synced_by):
    if synced_by:
        return "fa-user" if synced_by != "auto" else "fa-laptop"
    return "fa-question"


@register.filter
def dictget(dict, key):
    if key in dict:
        return dict[key]
    return ""

