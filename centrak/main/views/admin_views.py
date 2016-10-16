from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q, Count

from ezaddress.models import State
from core.models import BusinessLevel, BusinessOffice, Organisation, \
        Voltage, Station, Powerline 
from core.forms import OrganisationForm, OfficeForm
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


def get_station_type_id(tab_key):
    if tab_key in (None, '', 'transmission'):
        return Station.TRANSMISSION
    return (Station.INJECTION if tab_key == 'injection' else Station.DISTRIBUTION)


#: ==+: admin view functions
@login_required
def admin_home(request):
    return render(request, 'main/admin/index.html')


@login_required
def org_info(request):
    org = get_org_or_create_default()
    regions = BusinessOffice.objects.filter(level=BusinessLevel.LEVEL1)\
                            .annotate(num_points=Count('businessoffice'))\
                            .order_by('code')
                            

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
            messages.error(request, str(ex), extra_tags='danger')
    else:
        form = OrganisationForm(instance=org)
        
    return render(request, 'main/admin/org_form.html', {
        'form': form
    })


@login_required
def offices_home(request):
    offices = BusinessOffice.objects.all().order_by('level', 'code')
    return render(request, 'main/admin/offices_home.html', {
        'offices': offices
    })


@login_required
def manage_region(request, region_code=None):
    region = BusinessOffice() 
    if region_code:
        region =  get_object_or_404(BusinessOffice, code=region_code)
    
    if request.method == 'POST':
        try:
            post_data = request.POST.copy()
            if not region_code:
                post_data['parent'] = None
                post_data['level'] = BusinessLevel.LEVEL1
            
            form = OfficeForm(data=post_data, instance=region)
            if form.is_valid():
                form.save()

                message = (utils.MSG_FMT_SUCCESS_UPD if region_code else utils.MSG_FMT_SUCCESS_ADD)
                messages.success(request, message % 'Region', extra_tags='success')
                return redirect(reverse('admin-org-detail'))
        except Exception as ex:
            messages.error(request, str(ex), extra_tags='danger')
    else:
        form = OfficeForm(instance=region)
    return render(request, 'main/admin/office_form.html', {
        'form': form
    })

@login_required
def region_detail(request, region_code, tab=None):
    region = get_object_or_404(BusinessOffice, code=region_code)
    offices, powerlines = (None, None)

    if not tab or tab == 'points':
        query = Q(level=BusinessLevel.LEVEL2, parent=region.id)
        offices = BusinessOffice.objects.filter(query).order_by('code')
    elif tab == 'powerlines':
        pass

    return render(request, 'main/admin/region_detail.html', {
        'region': region, 'tab': tab,
        'offices': offices, 'powerlines': powerlines
    })


@login_required
def manage_office(request, office_code=None):
    office = BusinessOffice()
    if office_code:
        office = get_object_or_404(BusinessOffice, code=office_code)

    url_cancel = request.GET.get('@next', None)
    if request.method == 'POST':
        try:
            post_data = request.POST.copy()
            if not office_code:
                post_data['level'] = BusinessLevel.LEVEL2
            
            form = OfficeForm(data=post_data, instance=office)
            if form.is_valid():
                form.save()

                message = (utils.MSG_FMT_SUCCESS_UPD if office_code else utils.MSG_FMT_SUCCESS_ADD)
                messages.success(request, message % 'Service Point', extra_tags='success')
                return redirect(url_cancel or reverse('admin-org-detail'))
        except Exception as ex:
            messages.error(request, str(ex), extra_tags='danger')
    else:
        region_code = request.GET.get('for', None)
        if region_code:
            office.parent = get_object_or_404(BusinessOffice, code=region_code)
        form = OfficeForm(instance=office, url_cancel=url_cancel)

    return render(request, 'main/admin/office_form.html', {
        'form': form, 'is_spoint': True,
    })


@login_required
def office_detail(request, office_code=None):
    office = get_object_or_404(BusinessOffice, code=office_code)
    stations = None
    return render(request, 'main/admin/office_detail.html', {
        'office': office, 'stations': stations 
    })


@login_required
def powerstation_list(request, tab=None):
    station_type = get_station_type_id(tab)
    stations = Station.objects.filter(type=station_type).order_by('code')
    return render(request, 'main/admin/station_list.html', {
        'stations': stations, 'tab': tab
    })


@login_required
def powerline_list(request, tab=None):
    powerline_type = Powerline.FEEDER
    voltage = Voltage.MVOLTL if tab == '11' else Voltage.MVOLTH
    print([powerline_type, voltage])
    powerlines = Powerline.objects.filter(type=powerline_type, voltage=voltage)\
                          .order_by('code')
    return render(request, 'main/admin/powerline_list.html', {
        'powerlines': powerlines, 'tab': tab
    })
