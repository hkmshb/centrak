from django.shortcuts import render
from core.models import Organization, BusinessOffice
from core.utils import get_paged_object_list



def get_org_or_create_default():
    org = Organization.objects.first()
    if not org:
        org = dict(
            name='CenTrak', phone='', 
            url='www.centrak.org', email='info@centrak.org', 
            city='City'
        )
    return org


def org_info(request):
    org = get_org_or_create_default()
    offices = get_paged_object_list(request, BusinessOffice)
    return render(request, 'core/org-info.html', {
        'organization': org,
        'biz_offices': offices 
    })


def manage_org(request):
    pass

