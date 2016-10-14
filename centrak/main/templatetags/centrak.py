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
