from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from core.utils import MSG_FMT_SUCCESS_UPD
from core.utils import get_paged_object_list
from core.models import Organization, BusinessOffice
from core.forms import OrganizationForm




def get_org_or_create_default():
    org = Organization.objects.first()
    if not org:
        org = Organization(name='CenTrak',
                url='http://centrak.org', email='info@centrak.org',
                city='City')
    return org


def org_info(request):
    org = get_org_or_create_default()
    offices = get_paged_object_list(request, BusinessOffice)
    return render(request, 'core/org-info.html', {
        'organization': org,
        'biz_offices': offices 
    })


def manage_org(request):
    org = get_org_or_create_default()
    if request.method == 'POST':
        org_form = OrganizationForm(data=request.POST, instance=org)
        
        if org_form.is_valid():
            org_form.save()
            
            message = MSG_FMT_SUCCESS_UPD % 'Organization'
            messages.success(request, message, extra_tags='success')
            return redirect(reverse('org-info'))
    else:
        org_form = OrganizationForm(instance=org)
    return render(request, 'core/org-form.html', {
        'form': org_form
    })

