from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, forms as auth_forms
from django.core.urlresolvers import reverse
from django.db.models import Q, Count
from django.contrib import messages

from core.models import UserProfile, BusinessLevel, BusinessOffice, \
        Organisation, Voltage, Station, Powerline, ApiServiceInfo
from core.forms import OrganisationForm, OfficeForm, UserProfileForm, \
        ApiServiceInfoForm
from core.utils import admin_with_permission, has_object_permission, paginate
from .. import forms, handlers, tasks, utils



User = get_user_model()

#: ==+: util functions
def get_org_or_create_default():
    org = Organisation.objects.first()
    if not org:
        org = Organisation.objects.create(
                name='CENTrak', short_name='CENTrak', email='<info@centrak>',
                phone='<080-0000-0000>', website='<http://centrak>',
                addr_street='<Address Street>', addr_town='<Address Town>')
    return org


def get_station_type_id(tab_key):
    if tab_key in (None, '', 'transmission'):
        return Station.TRANSMISSION
    return (Station.INJECTION if tab_key == 'injection' else Station.DISTRIBUTION)



#: ==+: admin view functions
@admin_with_permission()
def admin_home(request):
    return render(request, 'main/admin/index.html')

@admin_with_permission()
def user_list(request):
    page = paginate(request, User.objects.all().order_by('last_name'))
    return render(request, 'main/admin/user_list.html', {
        'users': page
    })


@admin_with_permission()
def user_detail(request, user_id):
    """
    With appropriate permissions current user can change other user's passowrd
    to provide some sort of password reset function thus no need to know the
    current password. However, for the same user to change his own password, the
    old password must be supplied. 
    """
    user = get_object_or_404(User, pk=user_id)
    form_pwd = auth_forms.SetPasswordForm(user)
    if str(request.user.id) == user_id:
        form_pwd = auth_forms.PasswordChangeForm(user)
    
    # style password form
    attrs_ = {'class': 'form-control input-sm'}
    for fn in ['old_password', 'new_password1', 'new_password2']:
        field = form_pwd.fields.get(fn)
        if field:
            label = 'Confirm password' if '2' in fn else field.label
            attrs_['placeholder'] = label
            field.widget.attrs = attrs_.copy()
    
    return render(request, 'main/admin/user_detail.html', {
        'user': user, 'form_pwd': form_pwd
    })


@admin_with_permission()
def user_manage_passwd(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    is_same_user = request.user.id == user.id
    form_class = auth_forms.SetPasswordForm
    if is_same_user:
        form_class = auth_forms.PasswordChangeForm
    
    form = form_class(user, data=request.POST)
    if form.is_valid():
        form.save()

        msg_fmt = 'Password has been %s successfully'
        messages.success(request, msg_fmt % ('changed' if is_same_user else 'set'), 
                         extra_tags='success')
    else:
        messages.error(request, form.errors.as_text(), extra_tags='danger')

    return redirect(reverse('admin-user-info', args=[user_id]))


@admin_with_permission()
def manage_user(request, user_id=None):
    profile = UserProfile(user=User())
    if user_id:
        profile = get_object_or_404(UserProfile, user_id=user_id)
    
    kwargs = dict(instance=profile)
    if user_id:
        kwargs['initial'] = {
            'username': profile.user.username,
            'first_name': profile.user.first_name,
            'last_name': profile.user.last_name,
            'is_active': profile.user.is_active
        }

    if request.method == 'POST':
        try:
            form = UserProfileForm(data=request.POST, **kwargs)
            if form.is_valid():
                profile = form.save()
                
                message = (utils.MSG_FMT_SUCCESS_UPD if user_id else utils.MSG_FMT_SUCCESS_ADD)
                messages.success(request, message % 'User', extra_tags='success')
                return redirect(reverse('admin-user-info', args=[profile.user.id]))
        except Exception as ex:
            messages.error(request, str(ex), extra_tags='danger')
            raise ex
    else:
        form = UserProfileForm(**kwargs)
    return render(request, 'main/admin/user_form.html', {
        'form': form
    })


@admin_with_permission()
def apiservice_list(request):
    services = ApiServiceInfo.objects.all()
    return render(request, 'main/admin/apiservice_list.html', {
        'services': services
    })


@admin_with_permission()
def manage_apiservice(request, key=None):
    service = ApiServiceInfo()
    if key:
        service = get_object_or_404(ApiServiceInfo, key=key)
    
    if request.method == 'POST':
        try:
            form = ApiServiceInfoForm(data=request.POST, instance=service)
            if form.is_valid():
                service = form.save()
                
                message = utils.MSG_FMT_SUCCESS_UPD if key else utils.MSG_FMT_SUCCESS_ADD
                messages.success(request, message % 'External API Service', extra_tags='success')
                return redirect(reverse('admin-apiservice-info', args=[service.key]))
        except Exception as ex:
            messages.error(request, str(ex), extra_tags='danger')
    else:
        form = ApiServiceInfoForm(instance=service)
    return render(request, 'main/admin/apiservice_form.html', {
        'form': form
    })


@admin_with_permission()
def apiservice_detail(request, key):
    service = get_object_or_404(ApiServiceInfo, key=key)
    return render(request, 'main/admin/apiservice_detail.html', {
        'service': service
    })


@admin_with_permission()
def org_info(request):
    org = get_org_or_create_default()
    regions = BusinessOffice.objects.filter(level=BusinessLevel.LEVEL1)\
                            .annotate(num_points=Count('businessoffice'))\
                            .order_by('code')
    return render(request, 'main/admin/org_detail.html', {
        'org': org, 'regions': regions,
    })


@admin_with_permission('organisation.change_organisation')
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


@admin_with_permission()
def offices_home(request):
    offices = BusinessOffice.objects.all().order_by('level', 'code')
    return render(request, 'main/admin/offices_home.html', {
        'offices': offices
    })


@admin_with_permission('businessoffice.can_manage_region')
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

@admin_with_permission()
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


@admin_with_permission()
def manage_office(request, office_code=None):
    office = BusinessOffice()
    if office_code:
        office = get_object_or_404(BusinessOffice, code=office_code)
    
    # context (new, update) based permission checking
    perms = [f.format('businessoffice') for f in ['{0}.add_{0}', '{0}.change_{0}']]
    has_perm, denied_response = has_object_permission(request.user, office, *perms)
    if not has_perm: 
        return denied_response

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


@admin_with_permission()
def office_detail(request, office_code=None):
    office = get_object_or_404(BusinessOffice, code=office_code)
    stations = None
    return render(request, 'main/admin/office_detail.html', {
        'office': office, 'stations': stations 
    })


@admin_with_permission()
def powerstation_list(request, tab=None):
    station_type = get_station_type_id(tab)
    stations = Station.objects.filter(type=station_type).order_by('code')
    return render(request, 'main/admin/station_list.html', {
        'stations': stations, 'tab': tab
    })


@admin_with_permission()
def powerline_list(request, tab=None):
    powerline_type = Powerline.FEEDER
    voltage = Voltage.MVOLTL if tab == '11' else Voltage.MVOLTH
    powerlines = Powerline.objects.filter(type=powerline_type, voltage=voltage)\
                          .order_by('code')
    return render(request, 'main/admin/powerline_list.html', {
        'powerlines': powerlines, 'tab': tab
    })


@admin_with_permission()
def manage_imports(request, type):
    def get_task(name):
        task_name = 'import_%s' % name
        if not hasattr(tasks, task_name):
            message_fmt = "Task handler for `%s` import not found."
            raise ValueError(message_fmt % name.title())
        return getattr(tasks, task_name)

    form = forms.UploadFileForm()
    if request.method == 'POST':
        form = forms.UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            upl_obj = request.FILES['file']
            filepath = handlers.handle_uploaded_files(upl_obj)
            if not filepath:
                message = "Upload failed: %s" % upl_obj.name
                messages.error(request, message, extra_tags='danger')
                return redirect(reverse('admin-import', args=[type]))
            
            # tasks.import_accounts.delay(request.user.id, filepath)
            task = get_task(request.POST.get('tag'))
            task.delay(request.user.id, filepath)

            message = "Upload complete and import in progress. Check " \
                    + "notifications for resulting task status."
            messages.success(request, message, extra_tags='success')
        else:
            pass

    return render(request, 'main/admin/import_form.html', {
        'form': form, 'type': type
    })
