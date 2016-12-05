from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages

from core.utils import admin_with_permission, has_object_permission, \
        paginate
from core.models import ApiServiceInfo
from .forms import XFormForm
from .models import XForm, Account



@admin_with_permission()
def xform_list(request, tab=None):
    context, template = ({'tab': tab}, 'enumeration/admin/xform_list.html')
    if not tab or tab == 'imported':
        context['xforms'] = XForm.objects.order_by('object_id')
        return render(request, template, context)

    #: bootstrap env for js processing
    service = get_object_or_404(ApiServiceInfo, pk='survey')
    context['survey_api_root'] = service.api_root
    context['xforms_endpoint'] = reverse('xform-list')
    context['object_ids'] = [x.object_id for x in XForm.objects.only('object_id')]
    resp = render(request, 'enumeration/admin/xform_list.html', context)
    
    # include survey auth toke as cookies
    resp.set_cookie('survey_auth_token', service.api_token)
    return resp


@admin_with_permission()
def xform_detail(request, object_id):
    xform = XForm.objects.get(object_id=object_id)
    return render(request, 'enumeration/admin/xform_detail.html', {
        'xform': xform
    })


@admin_with_permission()
def manage_xform(request, object_id):
    xform = XForm.objects.get(object_id=object_id)
    if request.method == 'POST':
        form = XFormForm(data=request.POST)
        if form.is_valid():
            pass
    return render(request, 'enumeration/admin/xform_form.html', {
        'instance': xform
    })


@admin_with_permission()
def x__manage_xform(request, object_id):
    xform = XForm.objects.get(object_id=object_id)
    if request.method == 'POST':
        try:
            form = XFormForm(data=request.POST, instance=xform)
            if form.is_valid():
                form.save()

                message = "XForm updated successfully"
                messages.success(request, message, extra_tags='success')
                return redirect(reverse('admin-xform-info', args=[form.object_id]))
        except Exception as ex:
            messages.error(request, str(ex), extra_tags='danger')
    else:
        form = XFormForm(instance=xform)
    return render(request, 'enumeration/admin/xform_form.html', {
        'form': form
    })


@admin_with_permission()
def accounts_list(request):
    page = paginate(request, Account.objects.all())
    return render(request, 'enumeration/admin/account_list.html', {
        'accts': page
    })
