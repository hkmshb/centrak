from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from ezaddress.models import State
from core.models import BusinessLevel, Organisation, BusinessOffice
from ..forms import OrganisationForm
from .. import utils


#: ==+: util functions
def get_org_or_create_default():
    org = Organisation.objects.first()
    if not org:
        org = Organisation.objects.create(
                name='CENTrak', email='<info@centrak>',
                phone='<080-0000-0000>', website='<http://centrak>',
                addr_street='<Address Street>', addr_town='<Address Town>')
    return org


#: ==+: admin view functions
@login_required
def admin_home(request):
    return render(request, 'main/admin/index.html')


@login_required
def org_info(request):
    org = get_org_or_create_default()
    regions = BusinessOffice.objects.filter(level=BusinessLevel.LEVEL1)
    return render(request, 'main/admin/org_detail.html', {
        'org': org, 'regions': regions,
    })


@login_required
def manage_org(request):
    org = get_org_or_create_default()
    if request.method == 'POST':
        try:
            form = OrganisationForm(data=request.POST, instance=org)
            if form.is_valid():
                form.save()

                message = utils.MSG_FMT_SUCCESS_UPD % 'Organisation'
                messages.success(request, message, extra_tags='success')
                return redirect(reverse('admin-org-detail'))
        except Exception as ex:
            message = str(ex)
            messages.fail(request, message, extra_tags='danger')
    else:
        form = OrganisationForm(instance=org)
        
    return render(request, 'main/admin/org_form.html', {
        'form': form
    })
