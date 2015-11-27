from centrak.core.registry import register



@register.filter
def get_teammembership(person, team):
    return person.teammembership_set.get(team=team)


@register.filter
def member_count(teams):
    return sum([t.members.count() for t in teams.all()])


@register.filter
def device_count(teams):
    return sum([t.devices.count() for t in teams.all()])
