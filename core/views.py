from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from core.utils import MSG_FMT_SUCCESS_UPD, MSG_FMT_SUCCESS_ADD
from core.utils import get_paged_object_list, manage_object_deletion
from core.models import Organization, BusinessOffice
from core.forms import OrganizationForm, BusinessOfficeForm




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


def manage_office(request, id=None):
    office = (BusinessOffice() if not id else BusinessOffice.objects.get(pk=id))
    
    if request.method == 'POST':
        office_form = BusinessOfficeForm(data=request.POST, instance=office)
        
        if office_form.is_valid():
            office_form.save()
            
            msg_fmt = MSG_FMT_SUCCESS_ADD if not id else MSG_FMT_SUCCESS_UPD
            messages.success(request, msg_fmt % 'Business Office', extra_tags='success')
            
            urlname = ('org-info' if 'btn_save' in request.POST else 'office-create')
            return redirect(reverse(urlname))
    else:
        office_form = BusinessOfficeForm(instance=office)
    return render(request, 'core/office-form.html', {
        'form': office_form
    })


def delete_office(request, id=None):
    return manage_object_deletion(request, 
        BusinessOffice, 'business office(s)', 'org-info', id)

    