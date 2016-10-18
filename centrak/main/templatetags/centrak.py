from django import template
register = template.Library()


@register.filter
def urlcancel(form, default_url):
    if form.instance:
        if form.url_cancel:
            return form.url_cancel
        elif form.instance.id:
            return form.instance.get_absolute_url()            
    return default_url


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
