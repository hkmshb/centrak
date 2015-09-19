from django import template
register = template.Library()



@register.filter
def get_teammembership(person, team):
    return person.teammembership_set.get(team=team)

