import django_filters
from core.models import BusinessOffice



class BusinessOfficeFilter(django_filters.FilterSet):
    class Meta:
        model = BusinessOffice
        fields = ('level', 'parent',)

