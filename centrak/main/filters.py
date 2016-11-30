import django_filters_mongoengine as me_django_filters 
from enumeration.models import Capture



class CaptureFilter(me_django_filters.FilterSet):
    date_digitized = me_django_filters.DateFilter(lookup_type='exact')
    class Meta:
        model = Capture
        fields = ['book_code', 'tariff', 'date_digitized']
